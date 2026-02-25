from app.prompt_store import load_prompts, load_test_cases
from app.llm_runner import LLMRunner
from app.evaluator import evaluate_output
from app.regression import run_regression

def main():
    prompts = load_prompts()
    test_cases = load_test_cases()

    llm_runner = LLMRunner()

    results = run_regression(prompts, test_cases, llm_runner, evaluate_output)

    versions = list(results.keys())

    if len(versions) >= 2:
        v1, v2 = versions[0], versions[1]
        diff = results[v2] - results[v1]

        print("\n--- Regression Comparison ---")
        print(f"{v1} Score: {round(results[v1],3)}")
        print(f"{v2} Score: {round(results[v2],3)}")

        if diff > 0:
            print(f"{v2} improved by {round(diff, 3)}")
        elif diff < 0:
            print(f"{v2} regressed by {round(abs(diff), 3)}")
        else:
            print("No change detected.")

if __name__ == "__main__":
    main()