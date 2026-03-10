"""Tests for data models."""

import pytest
from datetime import datetime

from src.models.schemas import (
    EvaluationRule,
    TestCase,
    PromptVersion,
    EvaluationResult,
    TestCaseResult,
    PromptVersionResult,
    ToneType,
)


class TestEvaluationRule:
    """Tests for EvaluationRule model."""

    def test_create_valid_rule(self):
        rule = EvaluationRule(
            max_words=100,
            must_have_hashtags=3,
            tone=ToneType.PROFESSIONAL,
        )
        assert rule.max_words == 100
        assert rule.must_have_hashtags == 3
        assert rule.tone == ToneType.PROFESSIONAL

    def test_default_tone(self):
        rule = EvaluationRule(max_words=100, must_have_hashtags=3)
        assert rule.tone == ToneType.PROFESSIONAL

    def test_invalid_max_words(self):
        with pytest.raises(ValueError):
            EvaluationRule(max_words=0, must_have_hashtags=3)

    def test_negative_hashtags(self):
        with pytest.raises(ValueError):
            EvaluationRule(max_words=100, must_have_hashtags=-1)


class TestTestCase:
    """Tests for TestCase model."""

    def test_create_test_case(self, sample_evaluation_rules):
        tc = TestCase(
            id="test_1",
            input="AI in healthcare",
            expected_rules=sample_evaluation_rules,
        )
        assert tc.id == "test_1"
        assert tc.input == "AI in healthcare"

    def test_auto_generate_id(self, sample_evaluation_rules):
        tc = TestCase(
            input="Machine learning basics",
            expected_rules=sample_evaluation_rules,
        )
        assert tc.id == "machine_learning_basics"

    def test_empty_input_fails(self, sample_evaluation_rules):
        with pytest.raises(ValueError):
            TestCase(input="", expected_rules=sample_evaluation_rules)


class TestPromptVersion:
    """Tests for PromptVersion model."""

    def test_create_prompt_version(self):
        pv = PromptVersion(
            version="v1",
            template="Write about {topic}.",
        )
        assert pv.version == "v1"
        assert pv.template == "Write about {topic}."

    def test_format_template(self):
        pv = PromptVersion(
            version="v1",
            template="Write about {topic}. Include {count} items.",
        )
        result = pv.format(topic="AI", count=5)
        assert result == "Write about AI. Include 5 items."

    def test_created_at_default(self):
        pv = PromptVersion(version="v1", template="test")
        assert isinstance(pv.created_at, datetime)


class TestEvaluationResult:
    """Tests for EvaluationResult model."""

    def test_create_result(self):
        result = EvaluationResult(
            check_name="word_count",
            passed=True,
            score=1.0,
            details={"word_count": 50},
        )
        assert result.check_name == "word_count"
        assert result.passed is True
        assert result.score == 1.0

    def test_score_bounds(self):
        # Score should be between 0 and 1
        result = EvaluationResult(
            check_name="test",
            passed=True,
            score=0.5,
        )
        assert 0.0 <= result.score <= 1.0


class TestPromptVersionResult:
    """Tests for PromptVersionResult model."""

    def test_pass_rate_calculation(self):
        test_results = [
            TestCaseResult(
                test_case_id="t1",
                input="test1",
                generated_output="output1",
                evaluation_results=[],
                total_score=0.8,
                execution_time_ms=100,
            ),
            TestCaseResult(
                test_case_id="t2",
                input="test2",
                generated_output="output2",
                evaluation_results=[],
                total_score=0.5,
                execution_time_ms=100,
            ),
        ]
        
        result = PromptVersionResult(
            version="v1",
            test_results=test_results,
            average_score=0.65,
            total_tests=2,
            passed_tests=1,
            execution_time_ms=200,
        )
        
        assert result.pass_rate == 50.0

    def test_empty_tests_pass_rate(self):
        result = PromptVersionResult(
            version="v1",
            test_results=[],
            average_score=0.0,
            total_tests=0,
            passed_tests=0,
            execution_time_ms=0,
        )
        assert result.pass_rate == 0.0
