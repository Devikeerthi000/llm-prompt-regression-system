"""Data stores for prompts and test cases."""

from pathlib import Path
from typing import Iterator

from src.core.exceptions import DataLoadError
from src.data.loader import DataLoader
from src.models.schemas import TestCase, PromptVersion


class PromptStore:
    """
    Store for managing prompt versions.
    
    Provides an interface for loading, accessing, and iterating
    over prompt versions.
    """

    def __init__(self, path: Path | str | None = None) -> None:
        """
        Initialize prompt store.

        Args:
            path: Optional path to load prompts from
        """
        self._prompts: dict[str, PromptVersion] = {}
        if path:
            self.load(path)

    def load(self, path: Path | str) -> None:
        """Load prompts from file."""
        self._prompts = DataLoader.load_prompts(path)

    def get(self, version: str) -> PromptVersion | None:
        """Get a prompt version by ID."""
        return self._prompts.get(version)

    def add(self, prompt: PromptVersion) -> None:
        """Add a prompt version."""
        self._prompts[prompt.version] = prompt

    def remove(self, version: str) -> bool:
        """Remove a prompt version."""
        if version in self._prompts:
            del self._prompts[version]
            return True
        return False

    def versions(self) -> list[str]:
        """Get list of version IDs."""
        return list(self._prompts.keys())

    def __len__(self) -> int:
        return len(self._prompts)

    def __iter__(self) -> Iterator[PromptVersion]:
        return iter(self._prompts.values())

    def __contains__(self, version: str) -> bool:
        return version in self._prompts

    def items(self) -> Iterator[tuple[str, PromptVersion]]:
        """Iterate over (version, prompt) pairs."""
        return iter(self._prompts.items())


class TestCaseStore:
    """
    Store for managing test cases.
    
    Provides filtering, tagging, and iteration capabilities.
    """

    def __init__(self, path: Path | str | None = None) -> None:
        """
        Initialize test case store.

        Args:
            path: Optional path to load test cases from
        """
        self._test_cases: list[TestCase] = []
        if path:
            self.load(path)

    def load(self, path: Path | str) -> None:
        """Load test cases from file."""
        self._test_cases = DataLoader.load_test_cases(path)

    def add(self, test_case: TestCase) -> None:
        """Add a test case."""
        self._test_cases.append(test_case)

    def get_by_id(self, id: str) -> TestCase | None:
        """Get a test case by ID."""
        for tc in self._test_cases:
            if tc.id == id:
                return tc
        return None

    def filter_by_tags(self, tags: list[str]) -> list[TestCase]:
        """Get test cases matching any of the given tags."""
        return [
            tc for tc in self._test_cases
            if any(tag in tc.tags for tag in tags)
        ]

    def __len__(self) -> int:
        return len(self._test_cases)

    def __iter__(self) -> Iterator[TestCase]:
        return iter(self._test_cases)

    def __getitem__(self, index: int) -> TestCase:
        return self._test_cases[index]
