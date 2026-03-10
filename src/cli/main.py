"""Main CLI application using Typer."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from src import __version__
from src.cli.utils import print_banner, print_error, print_success
from src.config.settings import get_settings
from src.core.logging import setup_logging, get_logger
from src.data.store import PromptStore, TestCaseStore
from src.engine.runner import RegressionRunner
from src.engine.analyzer import RegressionAnalyzer
from src.engine.reporter import ReportGenerator
from src.evaluators.registry import get_default_evaluators
from src.providers.factory import create_provider

app = typer.Typer(
    name="promptguard",
    help="PromptGuard AI - LLM Prompt Quality & Regression Monitoring System",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"PromptGuard AI v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug mode.",
    ),
) -> None:
    """
    PromptGuard AI - LLM Prompt Quality & Regression Monitoring System.
    
    Automate evaluation, benchmarking, and regression detection for LLM prompts.
    """
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(level=log_level)


@app.command()
def run(
    prompts_file: Path = typer.Option(
        Path("data/prompt_versions.json"),
        "--prompts",
        "-p",
        help="Path to prompt versions file.",
        exists=True,
    ),
    tests_file: Path = typer.Option(
        Path("data/test_cases.json"),
        "--tests",
        "-t",
        help="Path to test cases file.",
        exists=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path for report (JSON or Markdown).",
    ),
    detailed: bool = typer.Option(
        False,
        "--detailed",
        help="Show detailed test results.",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Override LLM model to use.",
    ),
    threshold: float = typer.Option(
        0.05,
        "--threshold",
        help="Regression detection threshold.",
    ),
) -> None:
    """
    Run regression tests on prompt versions.
    
    Evaluates all prompt versions against test cases and detects regressions.
    """
    logger = get_logger(__name__)
    settings = get_settings()

    print_banner(console)

    try:
        # Load data
        with console.status("[bold blue]Loading data..."):
            prompt_store = PromptStore(prompts_file)
            test_store = TestCaseStore(tests_file)

        console.print(f"📋 Loaded [cyan]{len(prompt_store)}[/cyan] prompt versions")
        console.print(f"🧪 Loaded [cyan]{len(test_store)}[/cyan] test cases")
        console.print()

        # Create provider and evaluator
        provider_kwargs = {}
        if model:
            provider_kwargs["model"] = model

        provider = create_provider(settings=settings, **provider_kwargs)
        evaluator = get_default_evaluators(provider)

        console.print(f"🤖 Using model: [cyan]{provider.model}[/cyan]")
        console.print()

        # Run regression tests
        runner = RegressionRunner(
            llm_provider=provider,
            evaluator=evaluator,
            pass_threshold=settings.evaluation.pass_threshold,
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Running tests...",
                total=len(prompt_store) * len(test_store),
            )

            def update_progress(version: str, current: int, total: int) -> None:
                progress.update(task, advance=1, description=f"Testing {version}...")

            report = runner.run_regression(
                prompt_store,
                test_store,
                progress_callback=update_progress,
            )

        # Analyze results
        analyzer = RegressionAnalyzer(regression_threshold=threshold)
        report = analyzer.analyze_report(report)

        # Generate report
        reporter = ReportGenerator(console)
        reporter.print_summary(report)

        if detailed:
            reporter.print_detailed(report)

        # Print recommendation
        console.print()
        recommendation = analyzer.get_recommendation(report)
        console.print(f"[bold]{recommendation}[/bold]")

        # Save output
        if output:
            if output.suffix == ".json":
                reporter.save_json(report, output)
            else:
                reporter.save_markdown(report, output)
            print_success(console, f"Report saved to {output}")

    except Exception as e:
        logger.exception("Run failed")
        print_error(console, str(e))
        raise typer.Exit(1)


@app.command()
def validate(
    prompts_file: Path = typer.Option(
        Path("data/prompt_versions.json"),
        "--prompts",
        "-p",
        help="Path to prompt versions file.",
    ),
    tests_file: Path = typer.Option(
        Path("data/test_cases.json"),
        "--tests",
        "-t",
        help="Path to test cases file.",
    ),
) -> None:
    """
    Validate prompt and test case files without running tests.
    """
    print_banner(console)
    errors = []

    # Validate prompts
    try:
        if prompts_file.exists():
            store = PromptStore(prompts_file)
            print_success(console, f"Prompts file valid: {len(store)} versions")
        else:
            errors.append(f"Prompts file not found: {prompts_file}")
    except Exception as e:
        errors.append(f"Invalid prompts file: {e}")

    # Validate test cases
    try:
        if tests_file.exists():
            store = TestCaseStore(tests_file)
            print_success(console, f"Test cases file valid: {len(store)} test cases")
        else:
            errors.append(f"Test cases file not found: {tests_file}")
    except Exception as e:
        errors.append(f"Invalid test cases file: {e}")

    # Report errors
    if errors:
        for error in errors:
            print_error(console, error)
        raise typer.Exit(1)


@app.command()
def init(
    path: Path = typer.Argument(
        Path("."),
        help="Directory to initialize project in.",
    ),
) -> None:
    """
    Initialize a new PromptGuard project with sample files.
    """
    print_banner(console)

    data_dir = path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create sample prompts
    prompts_file = data_dir / "prompt_versions.json"
    if not prompts_file.exists():
        import json
        sample_prompts = {
            "v1": {
                "template": "Write a professional LinkedIn post about {topic}. Include 5 hashtags.",
                "description": "Basic prompt"
            },
            "v2": {
                "template": "Write a concise, engaging and professional LinkedIn post about {topic}. Use 3-5 relevant hashtags at the end.",
                "description": "Enhanced prompt with better instructions"
            }
        }
        prompts_file.write_text(json.dumps(sample_prompts, indent=2))
        print_success(console, f"Created {prompts_file}")

    # Create sample test cases
    tests_file = data_dir / "test_cases.json"
    if not tests_file.exists():
        import json
        sample_tests = [
            {
                "input": "AI in healthcare",
                "expected_rules": {
                    "max_words": 150,
                    "must_have_hashtags": 5,
                    "tone": "professional"
                }
            },
            {
                "input": "Startup fundraising tips",
                "expected_rules": {
                    "max_words": 120,
                    "must_have_hashtags": 3,
                    "tone": "professional"
                }
            }
        ]
        tests_file.write_text(json.dumps(sample_tests, indent=2))
        print_success(console, f"Created {tests_file}")

    # Create .env.example
    env_example = path / ".env.example"
    if not env_example.exists():
        env_example.write_text(
            "# PromptGuard AI Configuration\n"
            "GROQ_API_KEY=your_groq_api_key_here\n"
            "# OPENAI_API_KEY=your_openai_api_key_here\n"
            "# ANTHROPIC_API_KEY=your_anthropic_api_key_here\n"
        )
        print_success(console, f"Created {env_example}")

    console.print()
    console.print("[bold green]✅ Project initialized![/bold green]")
    console.print()
    console.print("Next steps:")
    console.print("  1. Copy .env.example to .env and add your API key")
    console.print("  2. Run [cyan]promptguard run[/cyan] to test your prompts")


if __name__ == "__main__":
    app()
