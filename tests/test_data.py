"""Tests for data loading."""

import json
import pytest
from pathlib import Path

from src.data.loader import DataLoader
from src.data.store import PromptStore, TestCaseStore
from src.core.exceptions import DataLoadError


class TestDataLoader:
    """Tests for DataLoader."""

    def test_load_test_cases_json(self, sample_tests_file):
        test_cases = DataLoader.load_test_cases(sample_tests_file)
        
        assert len(test_cases) == 2
        assert test_cases[0].input == "AI in healthcare"
        assert test_cases[0].expected_rules.max_words == 150

    def test_load_prompts_json(self, sample_prompts_file):
        prompts = DataLoader.load_prompts(sample_prompts_file)
        
        assert len(prompts) == 2
        assert "v1" in prompts
        assert "v2" in prompts
        assert "{topic}" in prompts["v1"].template

    def test_file_not_found(self, temp_data_dir):
        with pytest.raises(DataLoadError) as exc_info:
            DataLoader.load_test_cases(temp_data_dir / "nonexistent.json")
        
        assert "not found" in str(exc_info.value).lower()

    def test_invalid_json(self, temp_data_dir):
        invalid_file = temp_data_dir / "invalid.json"
        invalid_file.write_text("{ invalid json }")
        
        with pytest.raises(DataLoadError):
            DataLoader.load_test_cases(invalid_file)

    def test_load_yaml(self, temp_data_dir):
        yaml_file = temp_data_dir / "tests.yaml"
        yaml_file.write_text("""
- input: "Test topic"
  expected_rules:
    max_words: 100
    must_have_hashtags: 3
    tone: professional
""")
        
        test_cases = DataLoader.load_test_cases(yaml_file)
        assert len(test_cases) == 1
        assert test_cases[0].input == "Test topic"


class TestPromptStore:
    """Tests for PromptStore."""

    def test_load_from_file(self, sample_prompts_file):
        store = PromptStore(sample_prompts_file)
        
        assert len(store) == 2
        assert "v1" in store
        assert "v2" in store

    def test_get_prompt(self, sample_prompts_file):
        store = PromptStore(sample_prompts_file)
        
        prompt = store.get("v1")
        assert prompt is not None
        assert prompt.version == "v1"

    def test_get_nonexistent(self, sample_prompts_file):
        store = PromptStore(sample_prompts_file)
        
        prompt = store.get("v999")
        assert prompt is None

    def test_iterate_prompts(self, sample_prompts_file):
        store = PromptStore(sample_prompts_file)
        
        versions = [p.version for p in store]
        assert "v1" in versions
        assert "v2" in versions


class TestTestCaseStore:
    """Tests for TestCaseStore."""

    def test_load_from_file(self, sample_tests_file):
        store = TestCaseStore(sample_tests_file)
        
        assert len(store) == 2

    def test_get_by_id(self, sample_tests_file):
        store = TestCaseStore(sample_tests_file)
        
        # IDs are auto-generated from input
        tc = store.get_by_id(store[0].id)
        assert tc is not None
        assert tc.input == "AI in healthcare"

    def test_filter_by_tags(self, temp_data_dir):
        # Create test cases with tags
        tests = [
            {
                "input": "AI topic",
                "tags": ["ai", "tech"],
                "expected_rules": {"max_words": 100, "must_have_hashtags": 3, "tone": "professional"}
            },
            {
                "input": "Healthcare topic",
                "tags": ["healthcare"],
                "expected_rules": {"max_words": 100, "must_have_hashtags": 3, "tone": "professional"}
            },
        ]
        
        file_path = temp_data_dir / "tagged_tests.json"
        file_path.write_text(json.dumps(tests))
        
        store = TestCaseStore(file_path)
        filtered = store.filter_by_tags(["ai"])
        
        assert len(filtered) == 1
        assert filtered[0].input == "AI topic"

    def test_index_access(self, sample_tests_file):
        store = TestCaseStore(sample_tests_file)
        
        assert store[0].input == "AI in healthcare"
        assert store[1].input == "Cloud computing"
