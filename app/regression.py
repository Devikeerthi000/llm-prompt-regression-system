def run_regression(prompts, test_cases, llm_runner, evaluator):
    results = {}

    for version, data in prompts.items():
        total_score = 0
        total_tests = len(test_cases)

        print(f"\nRunning Prompt Version: {version}")

        for case in test_cases:
            topic = case["input"]
            rules = case["expected_rules"]

            prompt_text = data["template"].format(topic=topic)
            output = llm_runner.run(prompt_text)

            score = evaluator(output, rules, llm_runner)
            total_score += score

        average_score = total_score / (total_tests * 3)
        results[version] = average_score

        print(f"Average Score: {round(average_score, 3)}")

    return results