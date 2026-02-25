import re

def word_count_check(text, max_words):
    words = text.split()
    return len(words) <= max_words

def hashtag_count_check(text, required):
    hashtags = re.findall(r"#\w+", text)
    return len(hashtags) >= required

def tone_check(text, llm_runner):
    prompt = f"""
    Is the following text professional in tone?
    Answer only Yes or No.

    Text:
    {text}
    """

    response = llm_runner.run(prompt)
    return "yes" in response.lower()

def evaluate_output(text, rules, llm_runner):
    score = 0

    if word_count_check(text, rules["max_words"]):
        score += 1

    if hashtag_count_check(text, rules["must_have_hashtags"]):
        score += 1

    if tone_check(text, llm_runner):
        score += 1

    return score