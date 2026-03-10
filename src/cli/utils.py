"""CLI utility functions."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src import __version__


def print_banner(console: Console) -> None:
    """Print the application banner."""
    banner = Text()
    banner.append("PromptGuard AI", style="bold cyan")
    banner.append(" v" + __version__, style="dim")
    
    console.print()
    console.print(
        Panel(
            banner,
            subtitle="LLM Prompt Quality & Regression Monitoring",
            border_style="blue",
        )
    )
    console.print()


def print_error(console: Console, message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]❌ Error:[/bold red] {message}")


def print_success(console: Console, message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_warning(console: Console, message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(console: Console, message: str) -> None:
    """Print an info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")
