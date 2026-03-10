"""Tests for evaluators."""

import pytest
from unittest.mock import MagicMock

from src.evaluators.word_count import WordCountEvaluator
from src.evaluators.hashtag import HashtagEvaluator
from src.evaluators.tone import ToneEvaluator
from src.evaluators.composite import CompositeEvaluator
from src.providers.base import LLMResponse


class TestWordCountEvaluator:
    """Tests for WordCountEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return WordCountEvaluator()

    def test_within_limit(self, evaluator):
        text = "This is a short text with only ten words total."
        result = evaluator.evaluate(text, max_words=20)
        
        assert result.passed is True
        assert result.score == 1.0
        assert result.details["word_count"] == 10

    def test_exceeds_limit(self, evaluator):
        text = "This is a text that definitely exceeds the maximum word limit set."
        result = evaluator.evaluate(text, max_words=5)
        
        assert result.passed is False
        assert result.score < 1.0
        assert result.details["word_count"] == 12

    def test_exact_limit(self, evaluator):
        text = "exactly five words here now"
        result = evaluator.evaluate(text, max_words=5)
        
        assert result.passed is True
        assert result.score == 1.0

    def test_no_max_specified(self, evaluator):
        text = "Any text works without limit"
        result = evaluator.evaluate(text)
        
        assert result.passed is True
        assert result.score == 1.0


class TestHashtagEvaluator:
    """Tests for HashtagEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return HashtagEvaluator()

    def test_has_required_hashtags(self, evaluator):
        text = "Great post! #AI #ML #Tech #Innovation #Future"
        result = evaluator.evaluate(text, must_have_hashtags=5)
        
        assert result.passed is True
        assert result.score == 1.0
        assert result.details["hashtag_count"] == 5

    def test_missing_hashtags(self, evaluator):
        text = "Great post! #AI #ML"
        result = evaluator.evaluate(text, must_have_hashtags=5)
        
        assert result.passed is False
        assert result.score < 1.0
        assert result.details["hashtag_count"] == 2

    def test_no_hashtags_required(self, evaluator):
        text = "No hashtags needed here"
        result = evaluator.evaluate(text, must_have_hashtags=0)
        
        assert result.passed is True
        assert result.score == 1.0

    def test_exceeds_maximum(self, evaluator):
        text = "#One #Two #Three #Four #Five #Six"
        result = evaluator.evaluate(text, must_have_hashtags=3, max_hashtags=5)
        
        assert result.passed is False
        assert result.details["within_maximum"] is False


class TestToneEvaluator:
    """Tests for ToneEvaluator."""

    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            content="YES",
            model="test",
            provider="mock",
        )
        return provider

    def test_professional_tone_detected(self, mock_provider):
        evaluator = ToneEvaluator(llm_provider=mock_provider)
        result = evaluator.evaluate(
            "This is a professional analysis of market trends.",
            tone="professional"
        )
        
        assert result.passed is True
        assert result.score == 1.0
        mock_provider.generate.assert_called_once()

    def test_tone_not_detected(self, mock_provider):
        mock_provider.generate.return_value = LLMResponse(
            content="NO",
            model="test",
            provider="mock",
        )
        evaluator = ToneEvaluator(llm_provider=mock_provider)
        result = evaluator.evaluate("hey whats up lol", tone="professional")
        
        assert result.passed is False
        assert result.score == 0.0

    def test_empty_text(self, mock_provider):
        evaluator = ToneEvaluator(llm_provider=mock_provider)
        result = evaluator.evaluate("", tone="professional")
        
        assert result.passed is False
        mock_provider.generate.assert_not_called()


class TestCompositeEvaluator:
    """Tests for CompositeEvaluator."""

    def test_all_pass(self):
        evaluators = [
            WordCountEvaluator(),
            HashtagEvaluator(),
        ]
        composite = CompositeEvaluator(evaluators)
        
        text = "Short post #One #Two #Three"
        result = composite.evaluate(text, max_words=10, must_have_hashtags=3)
        
        assert result.passed is True
        assert result.score == 1.0

    def test_partial_pass(self):
        evaluators = [
            WordCountEvaluator(),
            HashtagEvaluator(),
        ]
        composite = CompositeEvaluator(evaluators)
        
        text = "Short post #One"  # Has words but not enough hashtags
        result = composite.evaluate(text, max_words=10, must_have_hashtags=5)
        
        assert result.passed is False
        assert 0 < result.score < 1.0

    def test_weighted_scoring(self):
        evaluators = [
            WordCountEvaluator(weight=2.0),
            HashtagEvaluator(weight=1.0),
        ]
        composite = CompositeEvaluator(evaluators)
        
        # Pass word count (weight 2), fail hashtags (weight 1)
        text = "Short post"
        result = composite.evaluate(text, max_words=10, must_have_hashtags=5)
        
        # Word count passes (1.0 * 2) + hashtag fails (0.0 * 1) / 3 = 0.67
        assert result.score == pytest.approx(2/3, rel=0.01)

    def test_add_evaluator(self):
        composite = CompositeEvaluator([])
        assert len(composite.evaluators) == 0
        
        composite.add_evaluator(WordCountEvaluator())
        assert len(composite.evaluators) == 1

    def test_remove_evaluator(self):
        composite = CompositeEvaluator([
            WordCountEvaluator(),
            HashtagEvaluator(),
        ])
        
        removed = composite.remove_evaluator("word_count")
        assert removed is True
        assert len(composite.evaluators) == 1
        assert composite.evaluators[0].name == "hashtags"
