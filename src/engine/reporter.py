"""Report generation utilities."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.models.schemas import RegressionReport, ComparisonResult


class ReportGenerator:
    """
    Generates formatted reports from regression results.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def print_summary(self, report: RegressionReport) -> None:
        """Print a summary of the regression report."""
        # Header
        self.console.print()
        self.console.print(
            Panel(
                f"[bold]Regression Report[/bold]\n"
                f"Run ID: {report.run_id}\n"
                f"Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                title="PromptGuard AI",
                border_style="blue",
            )
        )

        # Version results table
        table = Table(title="Version Results", show_header=True, header_style="bold cyan")
        table.add_column("Version", style="dim")
        table.add_column("Avg Score", justify="right")
        table.add_column("Pass Rate", justify="right")
        table.add_column("Tests", justify="right")
        table.add_column("Time (ms)", justify="right")

        for version, result in report.version_results.items():
            score_style = "green" if result.average_score >= 0.7 else "yellow" if result.average_score >= 0.5 else "red"
            is_best = version == report.best_version
            version_display = f"[bold]{version}[/bold] ★" if is_best else version

            table.add_row(
                version_display,
                f"[{score_style}]{result.average_score:.3f}[/{score_style}]",
                f"{result.pass_rate:.1f}%",
                str(result.total_tests),
                f"{result.execution_time_ms:.0f}",
            )

        self.console.print(table)

        # Comparisons
        if report.comparisons:
            self.console.print()
            self._print_comparisons(report.comparisons)

    def _print_comparisons(self, comparisons: list[ComparisonResult]) -> None:
        """Print comparison results."""
        self.console.print("[bold]Version Comparisons[/bold]")
        
        for comp in comparisons:
            if comp.is_regression:
                icon = "🔴"
                status = "REGRESSION"
                style = "red"
            elif comp.is_improvement:
                icon = "🟢"
                status = "IMPROVEMENT"
                style = "green"
            else:
                icon = "🟡"
                status = "NO CHANGE"
                style = "yellow"

            delta_sign = "+" if comp.score_delta >= 0 else ""
            self.console.print(
                f"  {icon} [{style}]{comp.baseline_version} → {comp.candidate_version}[/{style}]: "
                f"{delta_sign}{comp.score_delta:.3f} ({status})"
            )

    def print_detailed(self, report: RegressionReport) -> None:
        """Print detailed test results."""
        for version, result in report.version_results.items():
            self.console.print()
            self.console.print(f"[bold cyan]Version: {version}[/bold cyan]")
            
            table = Table(show_header=True, header_style="bold")
            table.add_column("Test Case")
            table.add_column("Score", justify="right")
            table.add_column("Checks", justify="center")
            table.add_column("Time (ms)", justify="right")

            for test_result in result.test_results:
                checks = []
                for eval_result in test_result.evaluation_results:
                    icon = "✓" if eval_result.passed else "✗"
                    checks.append(f"{icon}{eval_result.check_name[:1].upper()}")

                score_style = "green" if test_result.total_score >= 0.7 else "yellow" if test_result.total_score >= 0.5 else "red"

                table.add_row(
                    test_result.test_case_id[:30],
                    f"[{score_style}]{test_result.total_score:.3f}[/{score_style}]",
                    " ".join(checks),
                    f"{test_result.execution_time_ms:.0f}",
                )

            self.console.print(table)

    def save_json(self, report: RegressionReport, path: Path) -> None:
        """Save report as JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and handle datetime serialization
        data = report.model_dump()
        data["timestamp"] = report.timestamp.isoformat()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def save_markdown(self, report: RegressionReport, path: Path) -> None:
        """Save report as Markdown file."""
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "# Regression Report",
            "",
            f"**Run ID:** {report.run_id}",
            f"**Timestamp:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Best Version:** {report.best_version}",
            "",
            "## Version Results",
            "",
            "| Version | Avg Score | Pass Rate | Tests |",
            "|---------|-----------|-----------|-------|",
        ]

        for version, result in report.version_results.items():
            best_marker = " ⭐" if version == report.best_version else ""
            lines.append(
                f"| {version}{best_marker} | {result.average_score:.3f} | "
                f"{result.pass_rate:.1f}% | {result.total_tests} |"
            )

        if report.comparisons:
            lines.extend([
                "",
                "## Comparisons",
                "",
            ])
            for comp in report.comparisons:
                status = "🔴 Regression" if comp.is_regression else "🟢 Improvement" if comp.is_improvement else "🟡 No Change"
                lines.append(
                    f"- **{comp.baseline_version} → {comp.candidate_version}**: "
                    f"{comp.score_delta:+.3f} ({status})"
                )

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
