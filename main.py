from src.config.settings import get_settings
from src.core.logging import setup_logging
from src.data.store import PromptStore, TestCaseStore
from src.engine.analyzer import RegressionAnalyzer
from src.engine.reporter import ReportGenerator
from src.engine.runner import RegressionRunner
from src.evaluators.registry import get_default_evaluators
from src.providers.factory import create_provider


def main():
    # Setup
    settings = get_settings()
    setup_logging(level=settings.log_level)

    # Load data
    prompt_store = PromptStore(settings.data_dir / "prompt_versions.json")
    test_store = TestCaseStore(settings.data_dir / "test_cases.json")

    print(f"Loaded {len(prompt_store)} prompt versions, {len(test_store)} test cases")

    # Create provider and evaluator
    provider = create_provider(settings=settings)
    evaluator = get_default_evaluators(provider)

    print(f"Using model: {provider.model}")

    # Run regression
    runner = RegressionRunner(provider, evaluator, pass_threshold=settings.evaluation.pass_threshold)
    report = runner.run_regression(prompt_store, test_store)

    # Analyze
    analyzer = RegressionAnalyzer(regression_threshold=settings.evaluation.regression_threshold)
    report = analyzer.analyze_report(report)

    # Print results
    reporter = ReportGenerator()
    reporter.print_summary(report)

    # Recommendation
    print()
    print(analyzer.get_recommendation(report))


if __name__ == "__main__":
    main()