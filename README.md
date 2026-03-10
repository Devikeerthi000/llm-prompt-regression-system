<div align="center">

# 🛡️ PromptGuard AI

**Enterprise-Grade LLM Prompt Quality & Regression Monitoring System**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-green.svg)](https://pytest.org/)

*Automate prompt evaluation, benchmarking, and regression detection for production LLM systems.*

</div>

---

## 📸 Demo

<p align="center">
  <img src="assets/demo.png" width="700" alt="PromptGuard AI Demo"/>
</p>

---

## 🎯 What is PromptGuard AI?

When you update a prompt in your LLM application, how do you know the new version is actually better? PromptGuard AI answers that question automatically.

It takes your **prompt versions** and runs them against a set of **test cases** with defined quality rules — word count limits, required hashtags, tone expectations, and more. It then scores each version and compares them to detect **regressions** — cases where a newer prompt actually performs worse than the previous one.

Think of it as **unit testing, but for prompts.**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔄 **Version Comparison** | Compare multiple prompt versions side-by-side |
| 📊 **Regression Detection** | Automatically flag when a newer prompt scores lower |
| 🎛️ **Flexible Evaluators** | Word count, hashtag count, tone analysis, and custom checks |
| 🔌 **Provider Agnostic** | Works with Groq, OpenAI, Anthropic — swap with one config change |
| 📈 **Rich Reporting** | Clear CLI output with per-version scores and recommendations |
| 🧪 **Test Suite** | Fully tested with pytest |
| 🔒 **Type Safe** | Pydantic models and full type hints throughout |

---

## 🔄 How It Works

1. **Define prompt versions** — Write multiple versions of the same prompt in a JSON file, each with a different template and strategy.

2. **Create test cases** — Define inputs (topics) along with the quality rules each output must satisfy: max word count, minimum hashtags, expected tone, required keywords, etc.

3. **Run the regression engine** — PromptGuard sends each prompt version + each test case to the LLM, collects outputs, and evaluates them against the defined rules.

4. **Get scored results** — Each version receives a score (0.0 to 1.0) based on how many constraints its outputs satisfied.

5. **Regression detection** — If a newer version scores lower than the previous one, PromptGuard flags it as a regression and recommends against deploying it.

---

## 📊 Scoring & Regression Detection

Each test case output is evaluated against its defined constraints:

| Evaluator | What It Checks | Scoring |
|-----------|---------------|---------|
| **Word Count** | Output stays within the max word limit | Full or partial credit based on how close |
| **Hashtags** | Output contains the required number of hashtags | Proportional (e.g., 3 out of 5 = 0.6) |
| **Tone** | Output matches the expected tone (professional, casual, etc.) | LLM-based pass/fail |

The **average score** across all test cases determines the version's overall quality:

$$\text{Version Score} = \frac{\text{Total Points Earned}}{\text{Maximum Possible Points}}$$

A **regression** is flagged when:

$$\text{New Version Score} < \text{Previous Version Score} - \text{Threshold}$$

The default threshold is **5%**, meaning small fluctuations are tolerated but meaningful drops are caught.

---

## 📊 Example Results

| Version | Description | Avg Score | Status |
|---------|------------|-----------|--------|
| v1 | Basic prompt — just asks for a post with hashtags | 0.667 | Baseline |
| v2 | Added tone + length instructions | 0.833 | ✅ Improved |
| v3 | Restructured with role-playing preamble | 0.722 | ⚠️ Regression vs v2 |
| v4 | Refined with few-shot examples and strict constraints | 0.889 | ✅ Best so far |

PromptGuard would recommend deploying **v4** and flag **v3** as a regression point.

---

## 🏗️ Architecture

The system is built with a clean, modular design:

| Layer | Purpose | Key Modules |
|-------|---------|-------------|
| **CLI** | User interface via terminal commands | `src/cli/` |
| **Config** | Settings management with environment variables | `src/config/` |
| **Data** | Loading and storing prompt versions and test cases | `src/data/` |
| **Engine** | Running tests, analyzing results, generating reports | `src/engine/` |
| **Evaluators** | Pluggable quality checks (word count, hashtags, tone) | `src/evaluators/` |
| **Providers** | LLM integrations (Groq, OpenAI, etc.) | `src/providers/` |
| **Models** | Data schemas and type definitions | `src/models/` |

### Design Patterns Used

- **Strategy Pattern** — Evaluators are interchangeable; add new quality checks without touching existing code
- **Factory Pattern** — LLM providers are created through a factory, making it trivial to swap between Groq, OpenAI, etc.
- **Composite Pattern** — Multiple evaluators are combined into a single evaluation pipeline
- **Repository Pattern** — Data stores abstract away file I/O so the engine doesn't care where data comes from

### System Flow

```
Prompt Versions (JSON) ──→ Test Cases (JSON)
         │                        │
         └──────┬─────────────────┘
                ↓
         LLM Provider (Groq/OpenAI)
                ↓
         Constraint Evaluators
                ↓
         Regression Analyzer
                ↓
         CLI Report with Recommendations
```

---

## ⚙️ Tech Stack

| Technology | Role |
|-----------|------|
| **Python 3.11+** | Core language |
| **Groq API** | Default LLM provider (fast inference) |
| **Pydantic** | Data validation and settings management |
| **Typer + Rich** | Beautiful CLI interface |
| **pytest** | Testing framework |
| **Ruff** | Linting and formatting |
| **mypy** | Static type checking |

---

## 🎯 Why This Project Matters

Prompt engineering is no longer just about writing good prompts — it's about **maintaining them over time**. As teams iterate on prompts, subtle regressions creep in: a reworded instruction might reduce hashtag compliance, a restructured template might shift tone, or a "simplified" version might consistently exceed word limits.

PromptGuard AI brings **software engineering discipline** to prompt management:

- **Catch regressions before they hit production** — know exactly which prompt change degraded quality
- **Quantify prompt quality** — move beyond "this feels better" to measurable scores
- **Automate evaluation** — no more manual review of LLM outputs across versions
- **Document prompt evolution** — track how and why prompts changed over time

---

## 🔮 Future Improvements

- JSON and HTML report export for CI/CD pipeline integration
- Cost and latency tracking per prompt version
- Multi-model benchmarking (run the same prompts across different LLMs)
- A/B testing support with statistical significance checks
- Dashboard UI for visual regression tracking

---

<div align="center">


</div>
- Web dashboard (Streamlit / FastAPI)  
- Git-based prompt diff visualization  

---

## 👤 Author

Keerthi Adapa  
Email: keerthiadapa70@gmail.com  
GitHub: https://github.com/Devikeerthi000
