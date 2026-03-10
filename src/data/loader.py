"""Data loader with validation."""

import json
from pathlib import Path
from typing import Any

import yaml

from src.core.exceptions import DataLoadError
from src.core.logging import get_logger
from src.models.schemas import TestCase, PromptVersion, EvaluationRule

logger = get_logger(__name__)


class DataLoader:
    """
    Loads and validates data from files.
    
    Supports JSON and YAML formats with automatic schema validation.
    """

    @staticmethod
    def _load_file(path: Path) -> Any:
        """Load data from JSON or YAML file."""
        if not path.exists():
            raise DataLoadError(
                f"File not found: {path}",
                details={"path": str(path)},
            )

        try:
            with open(path, "r", encoding="utf-8") as f:
                if path.suffix in (".yaml", ".yml"):
                    return yaml.safe_load(f)
                return json.load(f)
        except json.JSONDecodeError as e:
            raise DataLoadError(
                f"Invalid JSON in {path}: {e}",
                details={"path": str(path), "error": str(e)},
            ) from e
        except yaml.YAMLError as e:
            raise DataLoadError(
                f"Invalid YAML in {path}: {e}",
                details={"path": str(path), "error": str(e)},
            ) from e

    @classmethod
    def load_test_cases(cls, path: Path | str) -> list[TestCase]:
        """
        Load and validate test cases from file.

        Args:
            path: Path to test cases file (JSON or YAML)

        Returns:
            List of validated TestCase objects

        Raises:
            DataLoadError: If file is invalid or validation fails
        """
        path = Path(path)
        logger.info(f"Loading test cases from {path}")

        data = cls._load_file(path)

        if not isinstance(data, list):
            raise DataLoadError(
                "Test cases file must contain a list",
                details={"path": str(path), "got": type(data).__name__},
            )

        test_cases: list[TestCase] = []
        for i, item in enumerate(data):
            try:
                # Convert expected_rules to EvaluationRule model
                if "expected_rules" in item:
                    item["expected_rules"] = EvaluationRule(**item["expected_rules"])
                test_cases.append(TestCase(**item))
            except Exception as e:
                raise DataLoadError(
                    f"Invalid test case at index {i}: {e}",
                    details={"index": i, "data": item, "error": str(e)},
                ) from e

        logger.info(f"Loaded {len(test_cases)} test cases")
        return test_cases

    @classmethod
    def load_prompts(cls, path: Path | str) -> dict[str, PromptVersion]:
        """
        Load and validate prompt versions from file.

        Args:
            path: Path to prompts file (JSON or YAML)

        Returns:
            Dictionary mapping version ID to PromptVersion

        Raises:
            DataLoadError: If file is invalid or validation fails
        """
        path = Path(path)
        logger.info(f"Loading prompts from {path}")

        data = cls._load_file(path)

        if not isinstance(data, dict):
            raise DataLoadError(
                "Prompts file must contain a dictionary",
                details={"path": str(path), "got": type(data).__name__},
            )

        prompts: dict[str, PromptVersion] = {}
        for version, item in data.items():
            try:
                if isinstance(item, dict):
                    prompts[version] = PromptVersion(
                        version=version,
                        template=item.get("template", ""),
                        description=item.get("description", ""),
                        metadata=item.get("metadata", {}),
                    )
                else:
                    # Simple format: just the template string
                    prompts[version] = PromptVersion(
                        version=version,
                        template=str(item),
                    )
            except Exception as e:
                raise DataLoadError(
                    f"Invalid prompt version '{version}': {e}",
                    details={"version": version, "data": item, "error": str(e)},
                ) from e

        logger.info(f"Loaded {len(prompts)} prompt versions")
        return prompts
