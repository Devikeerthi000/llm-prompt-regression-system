import json

def load_prompts(path="data/prompt_versions.json"):
    with open(path, "r") as f:
        return json.load(f)

def load_test_cases(path="data/test_cases.json"):
    with open(path, "r") as f:
        return json.load(f)