"""Tests for regression engine."""

import pytest
from unittest.mock import MagicMock, patch

from src.engine.runner import RegressionRunner
from src.engine.analyzer import RegressionAnalyzer
from src.evaluators.composite import CompositeEvaluator
from src.evaluators.word_count import WordCountEvaluator
from src.evaluators.hashtag import HashtagEvaluator
from src.models.schemas import PromptVersionResult, ComparisonResult
from src.data.store import PromptStore, TestCaseStore
from src.providers.base import LLMResponse


class TestRegressionRunner:
    """Tests for RegressionRunner."""

    @pytest.fixture
    def runner(self, mock_llm_provider):
        evaluator = CompositeEvaluator([
            WordCountEvaluator(),
            HashtagEvaluator(),
        ])
        return RegressionRunner(
            llm_provider=mock_llm_provider,
            evaluator=evaluator,
            pass_threshold=0.7,
        )

    def test_run_test_case(self, runner, sample_test_case, sample_prompt_version):
        result = runner.run_test_case(sample_test_case, sample_prompt_version)
        
        assert result.test_case_id == sample_test_case.id
        assert result.input == sample_test_case.input
        assert len(result.generated_output) > 0
        assert result.execution_time_ms > 0

    def test_run_version(self, runner, sample_prompt_version, sample_tests_file):
        test_store = TestCaseStore(sample_tests_file)
        
        result = runner.run_version(
            sample_prompt_version,
            list(test_store),
        )
        
        assert result.version == sample_prompt_version.version
        assert result.total_tests == len(test_store)
        assert 0 <= result.average_score <= 1.0

    def test_run_regression(
        self,
        runner,
        sample_prompts_file,
        sample_tests_file,
    ):
        prompt_store = PromptStore(sample_prompts_file)
        test_store = TestCaseStore(sample_tests_file)
        
        report = runner.run_regression(prompt_store, test_store)
        
        assert report.run_id is not None
        assert len(report.version_results) == len(prompt_store)
        assert report.best_version is not None


class TestRegressionAnalyzer:
    """Tests for RegressionAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        return RegressionAnalyzer(regression_threshold=0.05)

    def test_detect_regression(self, analyzer):
        baseline = PromptVersionResult(
            version="v1",
            test_results=[],
            average_score=0.8,
            total_tests=5,
            passed_tests=4,
            execution_time_ms=1000,
        )
        candidate = PromptVersionResult(
            version="v2",
            test_results=[],
            average_score=0.6,  # 0.2 drop = regression
            total_tests=5,
            passed_tests=3,
            execution_time_ms=1000,
        )
        
        comparison = analyzer.compare_versions(baseline, candidate)
        
        assert comparison.is_regression is True
        assert comparison.is_improvement is False
        assert comparison.score_delta == pytest.approx(-0.2)

    def test_detect_improvement(self, analyzer):
        baseline = PromptVersionResult(
            version="v1",
            test_results=[],
            average_score=0.6,
            total_tests=5,
            passed_tests=3,
            execution_time_ms=1000,
        )
        candidate = PromptVersionResult(
            version="v2",
            test_results=[],
            average_score=0.8,  # 0.2 improvement
            total_tests=5,
            passed_tests=4,
            execution_time_ms=1000,
        )
        
        comparison = analyzer.compare_versions(baseline, candidate)
        
        assert comparison.is_regression is False
        assert comparison.is_improvement is True
        assert comparison.score_delta == pytest.approx(0.2)

    def test_no_significant_change(self, analyzer):
        baseline = PromptVersionResult(
            version="v1",
            test_results=[],
            average_score=0.75,
            total_tests=5,
            passed_tests=4,
            execution_time_ms=1000,
        )
        candidate = PromptVersionResult(
            version="v2",
            test_results=[],
            average_score=0.77,  # 0.02 change < threshold
            total_tests=5,
            passed_tests=4,
            execution_time_ms=1000,
        )
        
        comparison = analyzer.compare_versions(baseline, candidate)
        
        assert comparison.is_regression is False
        assert comparison.is_improvement is False

    def test_get_recommendation_regression(self, analyzer):
        from src.models.schemas import RegressionReport
        from datetime import datetime
        
        report = RegressionReport(
            run_id="test",
            timestamp=datetime.now(),
            version_results={
                "v1": PromptVersionResult(
                    version="v1",
                    test_results=[],
                    average_score=0.8,
                    total_tests=5,
                    passed_tests=4,
                    execution_time_ms=1000,
                ),
                "v2": PromptVersionResult(
                    version="v2",
                    test_results=[],
                    average_score=0.5,
                    total_tests=5,
                    passed_tests=2,
                    execution_time_ms=1000,
                ),
            },
            comparisons=[
                ComparisonResult(
                    baseline_version="v1",
                    candidate_version="v2",
                    baseline_score=0.8,
                    candidate_score=0.5,
                    score_delta=-0.3,
                    is_regression=True,
                    is_improvement=False,
                    threshold=0.05,
                )
            ],
        )
        
        recommendation = analyzer.get_recommendation(report)
        
        assert "REGRESSION" in recommendation
        assert "v2" in recommendation
