# Example Tool Recommendations for AI Router

This shows what you should expect when you run the evaluation prompts with LLMs.

## Phase 1: Quick Wins (Install This Week - 1-2 days)

### 1. **mypy** - Static Type Checker
```
Category: Type Safety
Install: pip install mypy

Why: Your code has <20% type hints. mypy will catch type errors before runtime.
     Critical for subprocess calls and file I/O which are error-prone.

Setup Time: 30 minutes
Configuration (mypy.ini):
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
disallow_incomplete_defs = False
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True

Usage:
mypy ai-router.py ai-router-enhanced.py ai-router-mlx.py ai-router-truenas.py ai-router-truenas-production.py

Pre-commit Hook:
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.7.0
  hooks:
    - id: mypy
      args: [--ignore-missing-imports]

Expected First Run: 50-100 new type errors to fix
Time to Fix: 3-4 hours
Impact: High - catches bugs before they happen
```

### 2. **bandit** - Security Vulnerability Scanner
```
Category: Security
Install: pip install bandit

Why: Your code has subprocess.run() calls that need input validation.
     Potential command injection vulnerabilities in model path handling.

Setup Time: 15 minutes
Configuration (.bandit):
[bandit]
exclude_dirs = tests,./.*,build,dist

Usage:
bandit -r ai-router*.py -f json > bandit-report.json

Key Issues It Will Find:
- B602: shell=True in subprocess (HIGH SEVERITY)
- B607: Partial path to subprocess (HIGH SEVERITY)
- B101: Assert statements (LOW SEVERITY)

Pre-commit Hook:
- repo: https://github.com/PyCQA/bandit
  rev: 1.7.5
  hooks:
    - id: bandit
      args: [-c, .bandit]

Expected First Run: 5-15 security issues
Time to Fix: 2-3 hours (most are easy refactoring)
Impact: Critical - prevents production vulnerabilities
```

### 3. **Black** - Code Formatter
```
Category: Style Consistency
Install: pip install black

Why: Consistent formatting, easier code reviews, better team collaboration
     Already runs successfully, but Black enforces consistent style

Setup Time: 5 minutes
Configuration (pyproject.toml):
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

Usage:
black ai-router*.py --check  # Check only
black ai-router*.py           # Format in-place

Pre-commit Hook:
- repo: https://github.com/psf/black
  rev: 23.12.0
  hooks:
    - id: black
      language_version: python3.10

Expected First Run: Reformats code, no manual work
Time to Fix: 0 hours (automatic)
Impact: Medium - improves readability and consistency
```

---

## Phase 2: Core Quality Tools (Install Sprint 2 - 2-3 days)

### 4. **pytest** - Testing Framework
```
Category: Testing & Quality
Install: pip install pytest pytest-cov

Why: Your code has many branches (model selection, error handling) that need tests.
     Current test coverage: 0%
     Target test coverage: 70%

Setup Time: 2 hours
Configuration (pyproject.toml):
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
addopts = "-v --tb=short --cov=. --cov-report=html --cov-report=term-missing"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests",
]

Example Test File:
# tests/test_model_database.py
import pytest
from ai_router import ModelDatabase

def test_detect_use_case_coding():
    """Test coding use case detection"""
    result = ModelDatabase.detect_use_case("write a python function")
    assert result == "coding"

def test_recommend_model_coding():
    """Test model recommendation for coding"""
    model_id, model_data = ModelDatabase.recommend_model("coding")
    assert "name" in model_data
    assert "speed" in model_data

Usage:
pytest tests/ -v --cov=.

Pre-commit Hook:
- repo: local
  hooks:
    - id: pytest
      name: pytest
      entry: pytest tests/
      language: system
      pass_filenames: false
      always_run: true

Expected First Run: 0 tests, setup infrastructure
Time to Write Tests: 1 sprint
Impact: High - prevents regressions, documents expected behavior
```

### 5. **pylint** - Code Analysis
```
Category: Code Quality Analysis
Install: pip install pylint

Why: Catches code smells and design issues beyond style.
     Detects unused variables, unreachable code, missing documentation.

Setup Time: 45 minutes
Configuration (.pylintrc):
[MASTER]
ignore-patterns=test_.*?py
[MESSAGES CONTROL]
disable=
    C0111,  # missing-docstring (too strict)
    C0103,  # invalid-name (conflicts with naming conventions)
    R0913,  # too-many-arguments
    R0914,  # too-many-locals
    W0212,  # protected-access (internal APIs)
[DESIGN]
max-attributes=10
max-arguments=5
max-locals=15

Usage:
pylint ai-router.py --exit-zero > pylint-report.txt
pylint ai-router*.py --generate-rcfile > .pylintrc

Pre-commit Hook:
- repo: https://github.com/PyCQA/pylint
  rev: pylint-3.0.3
  hooks:
    - id: pylint
      args: [--exit-zero]

Expected First Run: 100-200 warnings and issues
Time to Fix: 1-2 days
Impact: Medium-High - improves overall code quality
```

### 6. **safety** - Dependency Vulnerability Scanner
```
Category: Security Dependencies
Install: pip install safety

Why: Check if any of your dependencies have known security vulnerabilities.
     Important for subprocess, GPUtil, psutil, Flask.

Setup Time: 10 minutes
Usage:
safety check --json > safety-report.json
safety check --full-report

Pre-commit Hook:
- repo: https://github.com/Lucas-C/pre-commit-hooks-safety
  rev: v1.1.2
  hooks:
    - id: python-safety-dependencies-check

Expected First Run: Varies by environment
Impact: High - ensures dependencies are secure
```

---

## Phase 3: Advanced Tools (Install Sprint 3+ - Ongoing)

### 7. **coverage.py** - Test Coverage Analysis
```
Install: pip install coverage
Usage:
coverage run -m pytest
coverage report
coverage html  # generates HTML report

Produces visual HTML report showing which lines are tested.
```

### 8. **sphinx** - Documentation Generation
```
Install: pip install sphinx
Purpose: Auto-generate docs from docstrings
Helps ensure documentation stays in sync with code
```

### 9. **ruff** - Fast Python Linter
```
Install: pip install ruff
Alternative to: flake8 + isort + pyupgrade
200x faster than flake8
Configuration (pyproject.toml):
[tool.ruff]
line-length = 88
target-version = "py310"
select = ["E", "F", "W", "I", "N"]
ignore = ["E501", "W503"]
```

### 10. **pre-commit** - Git Hook Framework
```
Install: pip install pre-commit
Purpose: Run all tools automatically before commits
Prevents bad code from entering repository
```

---

## Example GitHub Actions Workflow

Create `.github/workflows/code-quality.yml`:

```yaml
name: Code Quality Checks

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install mypy bandit pylint black pytest coverage

    - name: Format check with Black
      run: black --check ai-router*.py

    - name: Type check with mypy
      run: mypy ai-router*.py --ignore-missing-imports
      continue-on-error: true

    - name: Security check with Bandit
      run: bandit -r ai-router*.py -f json > bandit-report.json
      continue-on-error: true

    - name: Code analysis with pylint
      run: |
        pylint ai-router*.py --exit-zero | tee pylint-report.txt
      continue-on-error: true

    - name: Dependency check
      run: safety check --json > safety-report.json
      continue-on-error: true

    - name: Run tests
      run: pytest tests/ -v --cov=. --cov-report=xml
      continue-on-error: true

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        fail_ci_if_error: false
```

---

## Pre-commit Configuration

Create `.pre-commit-config.yaml`:

```yaml
# Install: pip install pre-commit
# Setup: pre-commit install
# Run manually: pre-commit run --all-files

repos:
  # Code formatting
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.10

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]
        additional_dependencies: [types-all]

  # Security
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-c, .bandit]

  # Import sorting
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort

  # General linting
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: check-added-large-files
      - id: trailing-whitespace
      - id: end-of-file-fixer
```

---

## Expected Results by Tool

| Tool | First Run Issues | Time to Fix | Ongoing Maintenance |
|------|-----------------|------------|-------------------|
| mypy | 50-100 | 3-4 hours | 10-15 min per PR |
| bandit | 5-15 | 2-3 hours | 5 min per PR |
| black | 0 (auto) | 0 | 0 (automatic) |
| pytest | setup | 1 sprint | ongoing |
| pylint | 100-200 | 1-2 days | 10-20 min per PR |
| safety | varies | 0-2 hours | 5 min per week |
| ruff | 0-20 | <1 hour | 5 min per PR |

---

## Success Metrics

**Before Tools**:
- 0% type hint coverage
- 0% test coverage
- 5-15 potential security issues
- 753+ style violations

**After Phase 1** (Week 1):
- 40% type hint coverage
- 10% test coverage
- 0 security issues
- 0 style violations

**After Phase 2** (Week 3):
- 70% type hint coverage
- 40% test coverage
- 0 security issues
- Complete pre-commit automation

**After Phase 3** (Week 4+):
- 90%+ type hint coverage
- 70%+ test coverage
- 0 security issues
- Automated quality reporting

---

## How to Use This Example

1. **Pick Phase 1 tools** (mypy, bandit, black)
2. **Install each one** as shown
3. **Create configuration files** in your repo root
4. **Run each tool** to see what issues it finds
5. **Fix issues in priority order** (security -> types -> style)
6. **Add to pre-commit** to prevent regressions
7. **Add to GitHub Actions** for automated checking
8. **Move to Phase 2** when Phase 1 is stable

**Estimated total time for full setup: 5-7 days**
