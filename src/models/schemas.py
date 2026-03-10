"""Pydantic models for type-safe data validation."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class ToneType(str, Enum):
    """Supported tone types for evaluation."""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"


class EvaluationRule(BaseModel):
    """Rules for evaluating LLM output."""

    max_words: int = Field(gt=0, description="Maximum allowed word count")
    must_have_hashtags: int = Field(ge=0, description="Minimum required hashtags")
    tone: ToneType = Field(default=ToneType.PROFESSIONAL, description="Expected tone")

    model_config = {"frozen": True}


class TestCase(BaseModel):
    """A single test case for prompt evaluation."""

    id: str = Field(default="", description="Unique test case identifier")
    input: str = Field(min_length=1, description="Input topic or content")
    expected_rules: EvaluationRule = Field(description="Evaluation rules to apply")
    description: str = Field(default="", description="Optional test case description")
    tags: list[str] = Field(default_factory=list, description="Tags for filtering")

    @model_validator(mode="after")
    def generate_id(self) -> "TestCase":
        if not self.id:
            self.id = self.input.lower().replace(" ", "_")[:30]
        return self


class PromptVersion(BaseModel):
    """A versioned prompt template."""

    version: str = Field(description="Version identifier (e.g., 'v1', 'v2.1')")
    template: str = Field(min_length=1, description="Prompt template with placeholders")
    description: str = Field(default="", description="Version description")
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def format(self, **kwargs: Any) -> str:
        """Format the template with provided variables."""
        return self.template.format(**kwargs)


class EvaluationResult(BaseModel):
    """Result of a single evaluation check."""

    check_name: str = Field(description="Name of the evaluation check")
    passed: bool = Field(description="Whether the check passed")
    score: float = Field(ge=0, le=1, description="Normalized score (0-1)")
    details: dict[str, Any] = Field(default_factory=dict, description="Check details")


class TestCaseResult(BaseModel):
    """Complete result for a single test case."""

    test_case_id: str = Field(description="Test case identifier")
    input: str = Field(description="Test input")
    generated_output: str = Field(description="LLM generated output")
    evaluation_results: list[EvaluationResult] = Field(description="Individual check results")
    total_score: float = Field(ge=0, le=1, description="Overall normalized score")
    execution_time_ms: float = Field(ge=0, description="Execution time in milliseconds")
    error: str | None = Field(default=None, description="Error message if failed")


class PromptVersionResult(BaseModel):
    """Aggregated results for a prompt version."""

    version: str = Field(description="Prompt version identifier")
    test_results: list[TestCaseResult] = Field(description="Results per test case")
    average_score: float = Field(ge=0, le=1, description="Average score across tests")
    total_tests: int = Field(ge=0, description="Total number of tests run")
    passed_tests: int = Field(ge=0, description="Number of tests that passed")
    execution_time_ms: float = Field(ge=0, description="Total execution time")

    @property
    def pass_rate(self) -> float:
        """Calculate the pass rate as a percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100


class ComparisonResult(BaseModel):
    """Comparison between two prompt versions."""

    baseline_version: str = Field(description="Baseline version for comparison")
    candidate_version: str = Field(description="Candidate version being compared")
    baseline_score: float = Field(description="Baseline average score")
    candidate_score: float = Field(description="Candidate average score")
    score_delta: float = Field(description="Score difference (candidate - baseline)")
    is_regression: bool = Field(description="Whether candidate regressed")
    is_improvement: bool = Field(description="Whether candidate improved")
    threshold: float = Field(description="Regression threshold used")


class RegressionReport(BaseModel):
    """Complete regression analysis report."""

    run_id: str = Field(description="Unique run identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    version_results: dict[str, PromptVersionResult] = Field(description="Results by version")
    comparisons: list[ComparisonResult] = Field(default_factory=list)
    best_version: str | None = Field(default=None, description="Best performing version")
    summary: dict[str, Any] = Field(default_factory=dict, description="Summary statistics")
