"""Regression test runner."""

import time
import uuid
from datetime import datetime
from typing import Callable

from src.core.exceptions import EvaluationError
from src.core.logging import get_logger
from src.data.store import PromptStore, TestCaseStore
from src.evaluators.composite import CompositeEvaluator
from src.models.schemas import (
    TestCase,
    TestCaseResult,
    PromptVersion,
    PromptVersionResult,
    RegressionReport,
)
from src.providers.base import BaseLLMProvider

logger = get_logger(__name__)


class RegressionRunner:
    """
    Executes regression tests across prompt versions.
    
    Runs each test case against each prompt version and collects
    detailed results with metrics.
    """

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        evaluator: CompositeEvaluator,
        pass_threshold: float = 0.7,
    ) -> None:
        """
        Initialize regression runner.

        Args:
            llm_provider: LLM provider for generating outputs
            evaluator: Evaluator pipeline
            pass_threshold: Minimum score to consider a test passed
        """
        self.llm_provider = llm_provider
        self.evaluator = evaluator
        self.pass_threshold = pass_threshold

    def run_test_case(
        self,
        test_case: TestCase,
        prompt: PromptVersion,
    ) -> TestCaseResult:
        """
        Run a single test case with a prompt version.

        Args:
            test_case: Test case to run
            prompt: Prompt version to use

        Returns:
            TestCaseResult with output and evaluation
        """
        start_time = time.perf_counter()
        error: str | None = None
        generated_output = ""

        try:
            # Format prompt with test input
            formatted_prompt = prompt.format(topic=test_case.input)

            # Generate output
            response = self.llm_provider.generate(formatted_prompt)
            generated_output = response.content

            # Evaluate output
            eval_results = self.evaluator.evaluate_detailed(
                generated_output,
                max_words=test_case.expected_rules.max_words,
                must_have_hashtags=test_case.expected_rules.must_have_hashtags,
                tone=test_case.expected_rules.tone.value,
            )

            # Calculate total score
            total_score = sum(r.score for r in eval_results) / len(eval_results) if eval_results else 0.0

        except Exception as e:
            logger.error(f"Test case failed: {test_case.id} - {e}")
            error = str(e)
            eval_results = []
            total_score = 0.0

        execution_time = (time.perf_counter() - start_time) * 1000

        return TestCaseResult(
            test_case_id=test_case.id,
            input=test_case.input,
            generated_output=generated_output,
            evaluation_results=eval_results,
            total_score=total_score,
            execution_time_ms=execution_time,
            error=error,
        )

    def run_version(
        self,
        prompt: PromptVersion,
        test_cases: list[TestCase],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> PromptVersionResult:
        """
        Run all test cases for a prompt version.

        Args:
            prompt: Prompt version to test
            test_cases: Test cases to run
            progress_callback: Optional callback for progress updates

        Returns:
            PromptVersionResult with aggregated metrics
        """
        logger.info(f"Running tests for prompt version: {prompt.version}")
        
        results: list[TestCaseResult] = []
        total_time = 0.0

        for i, test_case in enumerate(test_cases):
            result = self.run_test_case(test_case, prompt)
            results.append(result)
            total_time += result.execution_time_ms

            if progress_callback:
                progress_callback(i + 1, len(test_cases))

        # Calculate aggregates
        avg_score = sum(r.total_score for r in results) / len(results) if results else 0.0
        passed_tests = sum(1 for r in results if r.total_score >= self.pass_threshold)

        return PromptVersionResult(
            version=prompt.version,
            test_results=results,
            average_score=avg_score,
            total_tests=len(results),
            passed_tests=passed_tests,
            execution_time_ms=total_time,
        )

    def run_regression(
        self,
        prompt_store: PromptStore,
        test_case_store: TestCaseStore,
        progress_callback: Callable[[str, int, int], None] | None = None,
    ) -> RegressionReport:
        """
        Run full regression test suite.

        Args:
            prompt_store: Store containing prompt versions
            test_case_store: Store containing test cases
            progress_callback: Optional callback(version, current, total)

        Returns:
            Complete RegressionReport
        """
        run_id = str(uuid.uuid4())[:8]
        logger.info(f"Starting regression run: {run_id}")

        test_cases = list(test_case_store)
        version_results: dict[str, PromptVersionResult] = {}

        for version, prompt in prompt_store.items():
            def version_progress(current: int, total: int) -> None:
                if progress_callback:
                    progress_callback(version, current, total)

            result = self.run_version(prompt, test_cases, version_progress)
            version_results[version] = result

        # Find best version
        best_version = max(
            version_results.keys(),
            key=lambda v: version_results[v].average_score,
        ) if version_results else None

        report = RegressionReport(
            run_id=run_id,
            timestamp=datetime.now(),
            version_results=version_results,
            best_version=best_version,
            summary={
                "total_versions": len(version_results),
                "total_test_cases": len(test_cases),
                "best_score": version_results[best_version].average_score if best_version else 0.0,
            },
        )

        logger.info(f"Regression run complete: {run_id}")
        return report
