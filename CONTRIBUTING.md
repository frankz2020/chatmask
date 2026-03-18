# Contributing to chatmask

Thank you for your interest in contributing! This document explains how to get set up, what's in scope, and how the review process works.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [What's in Scope](#whats-in-scope)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Commit Messages](#commit-messages)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## Code of Conduct

This project follows a [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating you agree to abide by its terms.

---

## Getting Started

1. **Fork** the repository and clone your fork.
2. Follow the [installation steps in the README](README.md#installation) to get a working local setup.
3. Create a branch for your change: `git checkout -b your-feature-or-fix`.

---

## What's in Scope

The project is intentionally small and focused. Contributions that fit well include:

- **New element types** — e.g. phone numbers, timestamps, reaction counts
- **New pixelation styles** — e.g. solid fill, redaction bar, emoji overlay
- **Improved prompt robustness** — better detection across edge-case UIs
- **Performance improvements** — e.g. async/parallel image processing
- **Bug fixes** — anything broken or incorrect
- **Documentation** — clearer explanations, more examples
- **Tests** — unit tests for `pixelate.py`, `prompts.py`, etc.

Out of scope (for now): web interface, GUI, video support, packaging as a pip-installable library. Open a discussion first if you want to tackle something significant.

---

## How to Contribute

### Reporting bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml). Include your Python version, OS, and the exact command you ran.

### Suggesting features

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml). Explain the problem you're trying to solve, not just the solution.

### Submitting code

1. Open an issue first for non-trivial changes so we can align before you write code.
2. Make your changes on a feature branch.
3. Open a pull request against `main` using the [PR template](.github/PULL_REQUEST_TEMPLATE.md).

---

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/chatmask.git
cd chatmask

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (linting, formatting)
pip install ruff

# Copy and configure the API key
cp .env.example .env
# Edit .env: OPENROUTER_API_KEY=sk-or-v1-...
```

### Running the linter

```bash
ruff check .
ruff format --check .
```

### Running a quick smoke test

```bash
# Put one or two test screenshots (with no real PII) in ./test_input
python process.py ./test_input ./test_output
```

---

## Coding Guidelines

- **Python 3.10+** — use modern syntax (union types with `|`, `match`, etc.) where it adds clarity.
- **No external dependencies** beyond what's in `requirements.txt` unless there's a compelling reason.
- **Docstrings** — all public functions should have a one-line summary plus `Args` / `Returns` if non-obvious.
- **No print statements in library code** — `pixelate.py` and `prompts.py` are library modules; keep them pure. Console output belongs in `process.py` and `vision.py`.
- **Formatting** — use `ruff format` (88-char line length, double quotes).
- **No secrets in code** — never hardcode API keys, credentials, or personal data.

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) style:

```
<type>: <short summary>

[optional body]
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`.

Examples:

```
feat: add redaction-bar pixel mode (mode C)
fix: handle zero-dimension bbox returned by API
docs: add contributing guide
```

---

## Submitting a Pull Request

1. Push your branch and open a PR against `main`.
2. Fill in the [PR template](.github/PULL_REQUEST_TEMPLATE.md) — summary, type of change, how you tested it.
3. Make sure the CI checks pass (lint + import check).
4. A maintainer will review and may request changes. Please respond within a reasonable time.
5. Once approved, it will be squash-merged into `main`.

---

## Privacy Reminder

chatmask is a privacy tool. Please do **not** include real chat screenshots with personal information (names, profile pictures, messages) in test fixtures, examples, or PRs. Use synthetic or fully anonymized screenshots.
