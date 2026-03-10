"""Pytest configuration and fixtures."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.models.schemas import (
    EvaluationRule,
    TestCase,
    PromptVersion,
    ToneType,
)
from src.providers.base import BaseLLMProvider, LLMResponse


@pytest.fixture
def sample_evaluation_rules() -> EvaluationRule:
    """Sample evaluation rules fixture."""
    return EvaluationRule(
        max_words=150,
        must_have_hashtags=5,
        tone=ToneType.PROFESSIONAL,
    )


@pytest.fixture
def sample_test_case(sample_evaluation_rules: EvaluationRule) -> TestCase:
    """Sample test case fixture."""
    return TestCase(
        id="test_ai_healthcare",
        input="AI in healthcare",
        expected_rules=sample_evaluation_rules,
        description="Test case for AI healthcare topic",
        tags=["ai", "healthcare"],
    )


@pytest.fixture
def sample_prompt_version() -> PromptVersion:
    """Sample prompt version fixture."""
    return PromptVersion(
        version="v1",
        template="Write a professional LinkedIn post about {topic}. Include 5 hashtags.",
        description="Basic LinkedIn post prompt",
    )


@pytest.fixture
def mock_llm_provider() -> MagicMock:
    """Mock LLM provider fixture."""
    provider = MagicMock(spec=BaseLLMProvider)
    provider.provider_name = "mock"
    provider.model = "mock-model"
    provider.is_available.return_value = True
    
    # Default response
    provider.generate.return_value = LLMResponse(
        content="This is a professional test post about AI in healthcare. "
                "The future of medicine is being revolutionized by artificial intelligence. "
                "#AI #Healthcare #Innovation #Technology #Future",
        model="mock-model",
        provider="mock",
        usage={"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150},
        latency_ms=100.0,
    )
    
    return provider


@pytest.fixture
def sample_llm_response() -> LLMResponse:
    """Sample LLM response fixture."""
    return LLMResponse(
        content="This is a professional post about technology. #Tech #Innovation #AI #Future #Digital",
        model="test-model",
        provider="test",
        usage={"prompt_tokens": 20, "completion_tokens": 30, "total_tokens": 50},
        latency_ms=50.0,
    )


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Temporary data directory fixture."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def sample_prompts_file(temp_data_dir: Path) -> Path:
    """Create a sample prompts file."""
    import json
    
    prompts = {
        "v1": {
            "template": "Write about {topic}. Include 5 hashtags."
        },
        "v2": {
            "template": "Write an engaging post about {topic}. Use 3-5 hashtags."
        }
    }
    
    file_path = temp_data_dir / "prompts.json"
    file_path.write_text(json.dumps(prompts))
    return file_path


@pytest.fixture
def sample_tests_file(temp_data_dir: Path) -> Path:
    """Create a sample test cases file."""
    import json
    
    tests = [
        {
            "input": "AI in healthcare",
            "expected_rules": {
                "max_words": 150,
                "must_have_hashtags": 5,
                "tone": "professional"
            }
        },
        {
            "input": "Cloud computing",
            "expected_rules": {
                "max_words": 100,
                "must_have_hashtags": 3,
                "tone": "professional"
            }
        }
    ]
    
    file_path = temp_data_dir / "tests.json"
    file_path.write_text(json.dumps(tests))
    return file_path
