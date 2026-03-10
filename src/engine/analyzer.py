"""Regression analysis utilities."""

from src.core.logging import get_logger
from src.models.schemas import (
    RegressionReport,
    ComparisonResult,
    PromptVersionResult,
)

logger = get_logger(__name__)


class RegressionAnalyzer:
    """
    Analyzes regression reports to detect improvements and regressions.
    """

    def __init__(self, regression_threshold: float = 0.05) -> None:
        """
        Initialize analyzer.

        Args:
            regression_threshold: Score drop that indicates regression
        """
        self.regression_threshold = regression_threshold

    def compare_versions(
        self,
        baseline: PromptVersionResult,
        candidate: PromptVersionResult,
    ) -> ComparisonResult:
        """
        Compare two prompt versions.

        Args:
            baseline: Baseline version results
            candidate: Candidate version to compare

        Returns:
            ComparisonResult with analysis
        """
        delta = candidate.average_score - baseline.average_score
        is_regression = delta < -self.regression_threshold
        is_improvement = delta > self.regression_threshold

        return ComparisonResult(
            baseline_version=baseline.version,
            candidate_version=candidate.version,
            baseline_score=baseline.average_score,
            candidate_score=candidate.average_score,
            score_delta=delta,
            is_regression=is_regression,
            is_improvement=is_improvement,
            threshold=self.regression_threshold,
        )

    def analyze_report(self, report: RegressionReport) -> RegressionReport:
        """
        Add comparison analysis to a regression report.

        Args:
            report: Report to analyze

        Returns:
            Report with comparisons added
        """
        versions = list(report.version_results.keys())
        comparisons: list[ComparisonResult] = []

        # Compare consecutive versions
        for i in range(1, len(versions)):
            baseline = report.version_results[versions[i - 1]]
            candidate = report.version_results[versions[i]]
            comparison = self.compare_versions(baseline, candidate)
            comparisons.append(comparison)

            if comparison.is_regression:
                logger.warning(
                    f"Regression detected: {candidate.version} vs {baseline.version} "
                    f"(delta: {comparison.score_delta:+.3f})"
                )
            elif comparison.is_improvement:
                logger.info(
                    f"Improvement detected: {candidate.version} vs {baseline.version} "
                    f"(delta: {comparison.score_delta:+.3f})"
                )

        # Update report with comparisons
        report.comparisons = comparisons
        
        # Update summary
        report.summary.update({
            "regressions": sum(1 for c in comparisons if c.is_regression),
            "improvements": sum(1 for c in comparisons if c.is_improvement),
            "no_change": sum(1 for c in comparisons if not c.is_regression and not c.is_improvement),
        })

        return report

    def get_recommendation(self, report: RegressionReport) -> str:
        """
        Generate a recommendation based on analysis.

        Args:
            report: Analyzed regression report

        Returns:
            Recommendation string
        """
        if not report.version_results:
            return "No versions to analyze."

        if not report.comparisons:
            return f"Single version tested. Score: {report.version_results[report.best_version].average_score:.3f}"

        latest_comparison = report.comparisons[-1]

        if latest_comparison.is_regression:
            return (
                f"⚠️ REGRESSION DETECTED: {latest_comparison.candidate_version} "
                f"shows a {abs(latest_comparison.score_delta):.3f} drop from "
                f"{latest_comparison.baseline_version}. Consider reverting."
            )
        elif latest_comparison.is_improvement:
            return (
                f"✅ IMPROVEMENT: {latest_comparison.candidate_version} "
                f"shows a {latest_comparison.score_delta:.3f} improvement over "
                f"{latest_comparison.baseline_version}. Safe to deploy."
            )
        else:
            return (
                f"➡️ NO SIGNIFICANT CHANGE: {latest_comparison.candidate_version} "
                f"performs similarly to {latest_comparison.baseline_version}."
            )
