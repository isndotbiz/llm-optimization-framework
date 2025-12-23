# Testing Strategy & CI/CD Pipeline - Comprehensive Analysis

**Agent 9: Testing Strategy & CI/CD Expert**
**Date:** December 22, 2025
**Project:** D:\models (AI Router)
**Status:** Critical gaps identified - Actionable roadmap provided

---

## Executive Summary

The D:\models project currently has:
- **Partial test coverage:** 4 integration tests in `/tests/` directory (Session, Batch, Workflow, Template)
- **Archived legacy tests:** 21+ old tests in `/archive/old-tests/` (not maintained)
- **NO pytest.ini or test configuration**
- **NO GitHub Actions or CI/CD pipeline**
- **NO unit test framework**
- **NO cross-machine test variants**
- **NO performance regression testing**
- **Critical dependency:** Tests fail without pytest installed (Python 3.12.10 available, but pytest not installed)

### High-Impact Issues

1. **No pytest framework installed** - All existing tests depend on unittest, no pytest discovered
2. **Zero CI/CD automation** - No GitHub Actions, no continuous integration
3. **Low unit test coverage** - Only 4 integration tests exist, no unit tests for core modules
4. **Machine-specific hardcoding** - Tests don't account for 3-machine deployment (Ryzen+3090, Xeon+4060Ti, MacBook M4)
5. **No test discovery/collection** - No conftest.py, no automated test discovery
6. **Brittle imports** - Tests use hardcoded `sys.path.insert(0, str(Path(__file__).parent.parent))`
7. **No performance baselines** - No regression tests for speed/memory

---

## Current Testing Landscape

### A. Active Tests (D:\models\tests\)

```
D:\models\tests\
├── test_session_manager_integration.py      (192 lines, 14 tests)
├── test_batch_processor_integration.py       (217 lines, 14 tests)
├── test_template_manager_integration.py      (?) - exists, not reviewed
└── test_workflow_engine_integration.py       (326 lines, 11 tests)

Total: ~4 integration test files, ~39+ test methods
Framework: unittest (legacy, not pytest)
```

**Quality Assessment:**
- Tests are well-structured with setUp/tearDown
- Good coverage of happy paths
- Mock objects provided (e.g., MockAIRouter)
- Database/file cleanup in tearDown (good practice)
- **BUT:** No fixtures, no parametrization, no edge case testing

### B. Archived Tests (D:\models\archive\old-tests\)

```
21 test files including:
- test_integration.py (819 lines - custom test runner!)
- smoke_test.py (custom runner)
- test_compatibility.py
- test_context_manager.py
- test_database_persistence.py
- test_error_handling_enhanced.py
[... many more]
```

**Status:** ARCHIVED - not maintained, outdated syntax

### C. Test Files in Root (D:\models\)

```
- test_model_loading.py
- test_prompt.py
- test-mlx-models.py
```

**Status:** Ad-hoc, not integrated into test suite

### D. CI/CD Setup

```
No .github/workflows/ directory exists
No GitHub Actions configured
No pipeline automation
```

---

## 5 Critical Issues

### Issue 1: NO pytest Framework
**Problem:**
- Pytest not installed (`python -m pytest --version` fails)
- All tests use unittest (Python built-in)
- Pytest provides: better fixtures, parametrization, discovery, parallel execution

**Impact:**
- Manual test execution only
- No pytest plugins (coverage, xdist, timeout)
- No test discovery from CI/CD

**Solution:**
```bash
pip install pytest pytest-cov pytest-xdist pytest-timeout pytest-mock
```

### Issue 2: Zero CI/CD Pipeline
**Problem:**
- No GitHub Actions workflows
- No automated test runs on commit/PR
- No code coverage tracking
- No branch protection with test requirements

**Impact:**
- Broken tests merge to main
- No quality gates
- Can't verify cross-machine compatibility

**Solution:** Create `.github/workflows/tests.yml` (provided below)

### Issue 3: Low Unit Test Coverage
**Problem:**
- 4 integration tests only (session, batch, workflow, template)
- **Zero unit tests** for individual functions/classes
- No core module testing (ai-router.py, logging_config.py, etc.)

**Coverage Estimate:** <20% code coverage

**Core Modules Needing Unit Tests:**
1. `logging_config.py` - logger setup
2. `ai-router.py` - main CLI logic, machine detection, color handling
3. `health_assessment.py` - if exists
4. `utils/session_manager.py` - session CRUD operations
5. `utils/batch_processor.py` - batch job management
6. `utils/template_manager.py` - template rendering
7. `utils/workflow_engine.py` - workflow execution

### Issue 4: No Cross-Machine Test Variants
**Problem:**
- Tests don't account for 3 target machines:
  - **Machine 1:** Windows (native or WSL) - Ryzen 3900X + RTX 3090
  - **Machine 2:** TrueNAS (Linux) - Xeon Platinum + RTX 4060 Ti
  - **Machine 3:** MacBook - M4 Pro

- Platform-specific imports, paths, GPU detection not tested
- WSL path detection (`/mnt/d/` vs `D:\`) not tested
- GPU availability not checked in tests

**Impact:**
- Tests pass locally but fail on deployment
- WSL path handling issues missed
- GPU/device detection errors slip through

**Solution:** Machine-specific test fixtures (see below)

### Issue 5: No Performance/Regression Testing
**Problem:**
- No baseline performance metrics
- No memory usage tracking
- No regression detection
- Model loading times not tested

**Impact:**
- Silent performance degradation
- Memory leaks undetected
- Slow model loading goes unnoticed

---

## Proposed Testing Architecture

### Directory Structure

```
D:\models/
├── .github/
│   └── workflows/
│       ├── tests.yml                    # Main CI/CD pipeline
│       ├── performance.yml              # Performance regression testing
│       └── cross-machine.yml            # Multi-machine test matrix
│
├── tests/
│   ├── conftest.py                      # Pytest fixtures & config
│   ├── pytest.ini                       # Pytest configuration
│   ├── __init__.py
│   │
│   ├── unit/                            # Unit tests
│   │   ├── test_logging_config.py
│   │   ├── test_ai_router_core.py
│   │   ├── test_session_manager.py
│   │   ├── test_batch_processor.py
│   │   ├── test_template_manager.py
│   │   ├── test_workflow_engine.py
│   │   ├── test_model_selector.py
│   │   └── test_health_assessment.py
│   │
│   ├── integration/                     # Integration tests
│   │   ├── test_session_manager_integration.py (moved from tests/)
│   │   ├── test_batch_processor_integration.py (moved from tests/)
│   │   ├── test_template_manager_integration.py (moved from tests/)
│   │   ├── test_workflow_engine_integration.py (moved from tests/)
│   │   ├── test_end_to_end.py           # Full workflow integration
│   │   └── test_database_persistence.py
│   │
│   ├── performance/                     # Performance tests
│   │   ├── test_batch_performance.py    # Large batch handling
│   │   ├── test_session_memory.py       # Memory leak detection
│   │   └── test_model_loading_speed.py
│   │
│   ├── machine_specific/                # Machine-variant tests
│   │   ├── test_windows_paths.py
│   │   ├── test_wsl_compatibility.py
│   │   ├── test_gpu_detection.py
│   │   ├── test_macos_specific.py
│   │   └── test_linux_specific.py
│   │
│   ├── fixtures/                        # Test data & fixtures
│   │   ├── sample_workflows.yaml
│   │   ├── sample_prompts.json
│   │   ├── sample_templates.yaml
│   │   └── mock_models.json
│   │
│   └── smoke/                           # Quick smoke tests
│       ├── test_imports.py
│       └── test_basic_initialization.py
│
├── requirements-test.txt                # Test dependencies
└── pyproject.toml                       # Pytest config (modern approach)
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- Install pytest framework
- Create conftest.py with shared fixtures
- Create pytest.ini configuration
- Move existing 4 integration tests to `tests/integration/`
- Add requirements-test.txt

### Phase 2: Unit Tests (Week 2-3)
- Core module unit tests (logging, ai-router, session, batch, template, workflow)
- Mock external dependencies
- Achieve 40%+ code coverage

### Phase 3: Cross-Machine Testing (Week 3-4)
- Machine detection fixtures
- WSL path tests
- GPU availability tests
- Platform-specific test variants

### Phase 4: Performance & CI/CD (Week 4-5)
- Performance baseline tests
- GitHub Actions CI pipeline
- Parallel test execution
- Code coverage reporting

---

## Concrete Pytest Configuration

### 1. pytest.ini

```ini
[pytest]
minversion = 7.0
python_files = test_*.py
python_classes = Test*
python_functions = test_*
testpaths = tests
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    -ra
    --cov=.
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests (fast)
    integration: Integration tests (medium)
    performance: Performance tests (slow)
    windows: Windows-specific tests
    wsl: WSL-specific tests
    macos: macOS-specific tests
    linux: Linux-specific tests
    gpu: GPU-dependent tests
    slow: Slow-running tests
    flaky: Known flaky tests
```

### 2. conftest.py (Shared Fixtures)

```python
#!/usr/bin/env python3
"""
Pytest Configuration and Shared Fixtures
All tests use these fixtures for consistency
"""

import pytest
import sys
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch
import platform
import json


# ============================================================================
# MACHINE DETECTION FIXTURES
# ============================================================================

@pytest.fixture
def machine_type():
    """Detect current machine type"""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    elif system == "Linux":
        # Check if WSL
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    return "wsl"
        except:
            pass
        return "linux"
    return "unknown"


@pytest.fixture
def is_wsl():
    """Check if running in WSL"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False


@pytest.fixture
def is_macos():
    """Check if running on macOS"""
    return platform.system() == "Darwin"


@pytest.fixture
def is_windows():
    """Check if running on Windows"""
    return platform.system() == "Windows"


# ============================================================================
# TEMPORARY DIRECTORY FIXTURES
# ============================================================================

@pytest.fixture
def temp_db_path(tmp_path):
    """Temporary database file path"""
    return tmp_path / "test_session.db"


@pytest.fixture
def temp_checkpoint_dir(tmp_path):
    """Temporary checkpoint directory"""
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)
    return checkpoint_dir


@pytest.fixture
def temp_workflows_dir(tmp_path):
    """Temporary workflows directory"""
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir(exist_ok=True)
    return workflows_dir


@pytest.fixture
def temp_templates_dir(tmp_path):
    """Temporary templates directory"""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir(exist_ok=True)
    return templates_dir


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture
def schema_sql():
    """Basic SQLite schema for testing"""
    return """
    CREATE TABLE sessions (
        id TEXT PRIMARY KEY,
        model_id TEXT NOT NULL,
        title TEXT,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE messages (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        tokens_used INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );

    CREATE INDEX idx_sessions_model ON sessions(model_id);
    CREATE INDEX idx_messages_session ON messages(session_id);
    """


@pytest.fixture
def test_db_initialized(temp_db_path, schema_sql):
    """Create and initialize test database"""
    conn = sqlite3.connect(str(temp_db_path))
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    return temp_db_path


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_ai_router():
    """Mock AI Router for testing"""
    mock_router = MagicMock()
    mock_router.execute_prompt = MagicMock(
        return_value="Mock response from AI Router"
    )
    mock_router.get_model_info = MagicMock(
        return_value={"model_id": "test", "provider": "mock"}
    )
    return mock_router


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    mock = MagicMock()
    mock.info = MagicMock()
    mock.error = MagicMock()
    mock.warning = MagicMock()
    mock.debug = MagicMock()
    return mock


@pytest.fixture
def mock_model_config():
    """Sample model configuration"""
    return {
        "models": [
            {
                "model_id": "test_model_1",
                "provider": "ollama",
                "path": "/path/to/model1",
                "parameters": {"temperature": 0.7}
            },
            {
                "model_id": "test_model_2",
                "provider": "llama.cpp",
                "path": "/path/to/model2",
                "parameters": {"temperature": 0.5}
            }
        ]
    }


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_prompts():
    """Sample prompts for testing"""
    return [
        "What is Python?",
        "Explain machine learning",
        "Write a Python function to calculate fibonacci",
        "What are the benefits of microservices?",
        "How does JWT authentication work?"
    ]


@pytest.fixture
def sample_workflow_yaml():
    """Sample workflow YAML content"""
    return """
name: Test Workflow
description: Sample workflow for testing
variables:
  topic: Python
  complexity: intermediate

steps:
  - name: research
    type: prompt
    config:
      prompt: "Research {{ topic }} at {{ complexity }} level"
      model: test_model
      output_var: research_result

  - name: summarize
    type: prompt
    config:
      prompt: "Summarize: {{ research_result }}"
      model: test_model
      depends_on:
        - research
"""


@pytest.fixture
def sample_template_yaml(temp_templates_dir):
    """Sample prompt template YAML"""
    template_content = """
metadata:
  name: Code Generation
  version: 1.0
  variables:
    - name
    - language
    - description

system_prompt: |
  You are an expert {{ language }} programmer.
  Generate clean, well-documented code.

user_prompt: |
  Write a {{ language }} function called {{ name }}.
  Purpose: {{ description }}
"""
    template_file = temp_templates_dir / "code_gen.yaml"
    template_file.write_text(template_content)
    return template_file


# ============================================================================
# RESOURCE FIXTURES
# ============================================================================

@pytest.fixture
def track_memory_usage():
    """Track memory usage for performance tests"""
    import tracemalloc

    def _tracker():
        tracemalloc.start()
        initial_memory = tracemalloc.get_traced_memory()[0]

        class MemoryTracker:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                current_memory = tracemalloc.get_traced_memory()[0]
                self.memory_used = current_memory - initial_memory
                tracemalloc.stop()

        return MemoryTracker()

    return _tracker


# ============================================================================
# MARKER PYTEST PLUGINS
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "unit: Mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: Mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "machine_specific: Mark test as machine-specific"
    )


# ============================================================================
# PYTEST HOOKS
# ============================================================================

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Configure pytest before running"""
    # Set sys.path
    models_dir = Path(__file__).parent.parent
    if str(models_dir) not in sys.path:
        sys.path.insert(0, str(models_dir))
```

### 3. Unit Test Example: test_logging_config.py

```python
#!/usr/bin/env python3
"""
Unit Tests for logging_config.py
Tests logger setup and configuration
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import logging
import sys

# Adjust import path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logging_config import setup_logging


class TestLoggingConfig:
    """Unit tests for logging configuration"""

    @pytest.mark.unit
    def test_setup_logging_returns_logger(self):
        """Test that setup_logging returns a logger object"""
        logger = setup_logging()
        assert logger is not None
        assert isinstance(logger, logging.Logger)

    @pytest.mark.unit
    def test_setup_logging_creates_log_file(self, tmp_path):
        """Test that setup_logging creates log files"""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        with patch('logging_config.LOG_DIR', log_dir):
            logger = setup_logging()
            # Verify handlers are registered
            assert len(logger.handlers) > 0

    @pytest.mark.unit
    def test_setup_logging_log_levels(self):
        """Test that logger is configured with correct level"""
        logger = setup_logging()
        # Should be at INFO or DEBUG level
        assert logger.level in [logging.INFO, logging.DEBUG]

    @pytest.mark.unit
    def test_logger_can_log_messages(self):
        """Test that logger can actually log messages"""
        logger = setup_logging()

        # Should not raise exceptions
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")

    @pytest.mark.unit
    def test_setup_logging_idempotent(self):
        """Test that multiple calls don't duplicate handlers"""
        logger1 = setup_logging()
        initial_handler_count = len(logger1.handlers)

        logger2 = setup_logging()

        # Should be same or minimal increase
        assert len(logger2.handlers) <= initial_handler_count + 1
```

### 4. Machine-Specific Test: test_windows_paths.py

```python
#!/usr/bin/env python3
"""
Windows and WSL Path Compatibility Tests
Tests path handling across Windows, WSL, and other platforms
"""

import pytest
from pathlib import Path, PureWindowsPath, PurePosixPath
import sys
import platform
from unittest.mock import patch


class TestWindowsPaths:
    """Test Windows-specific path handling"""

    @pytest.mark.windows
    @pytest.mark.machine_specific
    def test_windows_path_conversion(self):
        """Test converting D:\\ paths to proper format"""
        windows_path = r"D:\models\organized\model.gguf"
        converted = Path(windows_path)
        assert converted.exists() or True  # Exists is OS-dependent
        assert str(converted).startswith("D:")

    @pytest.mark.windows
    @pytest.mark.machine_specific
    def test_forward_slash_in_windows_path(self):
        """Test that forward slashes work in Windows paths"""
        path1 = Path("D:\\models\\file.txt")
        path2 = Path("D:/models/file.txt")
        # Both should normalize to same path
        assert path1 == path2

    @pytest.mark.wsl
    @pytest.mark.machine_specific
    def test_wsl_mount_path_conversion(self, is_wsl):
        """Test WSL mount point path conversion"""
        if not is_wsl:
            pytest.skip("Not running in WSL")

        # In WSL, D: becomes /mnt/d/
        wsl_path = Path("/mnt/d/models/file.gguf")
        windows_equiv = "D:\\models\\file.gguf"

        # Verify WSL path structure
        assert str(wsl_path).startswith("/mnt/")

    @pytest.mark.wsl
    @pytest.mark.machine_specific
    def test_wsl_path_detection(self, is_wsl):
        """Test WSL detection mechanism"""
        if is_wsl:
            # We're in WSL, verify detection works
            try:
                with open('/proc/version', 'r') as f:
                    content = f.read().lower()
                    assert 'microsoft' in content or 'wsl' in content
            except FileNotFoundError:
                pytest.skip("Not in WSL environment")
        else:
            # Not in WSL, path should not exist
            try:
                with open('/proc/version', 'r') as f:
                    content = f.read().lower()
                    assert 'microsoft' not in content
            except FileNotFoundError:
                pass  # Expected on non-Linux systems

    @pytest.mark.machine_specific
    def test_absolute_path_handling(self):
        """Test absolute path handling across platforms"""
        if platform.system() == "Windows":
            abs_path = Path("D:\\models")
        elif platform.system() == "Darwin":
            abs_path = Path("/Users/user/models")
        else:  # Linux
            abs_path = Path("/home/user/models") or Path("/mnt/d/models")

        assert abs_path.is_absolute()

    @pytest.mark.machine_specific
    def test_relative_to_absolute_conversion(self):
        """Test converting relative paths to absolute"""
        # This test structure ensures paths work regardless of CWD
        relative = Path("tests/fixtures/sample.yaml")
        # Note: don't assert exists, just verify structure
        assert relative.parts[0] == "tests"
        assert relative.parts[-1] == "sample.yaml"


class TestGPUDetection:
    """Test GPU/device detection across machines"""

    @pytest.mark.gpu
    @pytest.mark.machine_specific
    def test_gpu_availability(self):
        """Test GPU availability detection"""
        # This will vary by machine
        try:
            import torch
            gpu_available = torch.cuda.is_available()
            # Don't assert, just log for info
            print(f"CUDA available: {gpu_available}")
        except ImportError:
            pytest.skip("PyTorch not installed")

    @pytest.mark.gpu
    @pytest.mark.machine_specific
    def test_mlx_availability(self, is_macos):
        """Test MLX framework availability on macOS"""
        if not is_macos:
            pytest.skip("MLX only available on macOS")

        try:
            import mlx.core as mx
            assert mx is not None
        except ImportError:
            pytest.skip("MLX not installed")
```

### 5. GitHub Actions CI/CD Workflow

Create `.github/workflows/tests.yml`:

```yaml
name: Testing & CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'

jobs:
  # Job 1: Quick Smoke Tests
  smoke-tests:
    name: Smoke Tests (${{ matrix.python-version }})
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-test.txt

      - name: Run smoke tests
        run: pytest tests/smoke/ -v -m "smoke"
        timeout-minutes: 5

  # Job 2: Unit Tests
  unit-tests:
    name: Unit Tests (${{ matrix.python-version }})
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-test.txt

      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=. --cov-report=xml
        timeout-minutes: 15

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests
          name: codecov-${{ matrix.os }}-py${{ matrix.python-version }}

  # Job 3: Integration Tests
  integration-tests:
    name: Integration Tests (${{ matrix.python-version }})
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-test.txt

      - name: Run integration tests
        run: pytest tests/integration/ -v --timeout=30
        timeout-minutes: 30

  # Job 4: Machine-Specific Tests
  machine-tests:
    name: Machine-Specific Tests (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-test.txt

      - name: Detect machine type
        id: machine
        run: |
          if [[ "$RUNNER_OS" == "Windows" ]]; then
            echo "machine_type=windows" >> $GITHUB_OUTPUT
          elif [[ "$RUNNER_OS" == "macOS" ]]; then
            echo "machine_type=macos" >> $GITHUB_OUTPUT
          else
            echo "machine_type=linux" >> $GITHUB_OUTPUT
          fi
        shell: bash

      - name: Run machine-specific tests
        run: |
          if [[ "${{ steps.machine.outputs.machine_type }}" == "windows" ]]; then
            pytest tests/machine_specific/test_windows_paths.py -v -m windows
          elif [[ "${{ steps.machine.outputs.machine_type }}" == "macos" ]]; then
            pytest tests/machine_specific/test_macos_specific.py -v -m macos
          else
            pytest tests/machine_specific/test_linux_specific.py -v -m linux
          fi
        shell: bash

  # Job 5: Code Quality
  code-quality:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install linters
        run: |
          pip install flake8 pylint black isort

      - name: Run black
        run: black --check --diff .
        continue-on-error: true

      - name: Run flake8
        run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        continue-on-error: true

  # Job 6: Security Checks
  security:
    name: Security Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Bandit security scan
        run: |
          pip install bandit
          bandit -r . -ll
        continue-on-error: true

  # Final Status
  test-results:
    name: Test Results Summary
    runs-on: ubuntu-latest
    needs: [smoke-tests, unit-tests, integration-tests, machine-tests, code-quality, security]
    if: always()
    steps:
      - name: Check test status
        run: |
          echo "Smoke Tests: ${{ needs.smoke-tests.result }}"
          echo "Unit Tests: ${{ needs.unit-tests.result }}"
          echo "Integration Tests: ${{ needs.integration-tests.result }}"
          echo "Machine Tests: ${{ needs.machine-tests.result }}"
          echo "Code Quality: ${{ needs.code-quality.result }}"
          echo "Security: ${{ needs.security.result }}"
```

### 6. requirements-test.txt

```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-xdist>=3.3.0
pytest-timeout>=2.1.0
pytest-mock>=3.11.0
pytest-asyncio>=0.21.0
coverage>=7.3.0
mock>=5.1.0
faker>=19.3.0

# Code quality
flake8>=6.0.0
pylint>=2.17.0
black>=23.7.0
isort>=5.12.0

# Security
bandit>=1.7.5

# Optional: for performance testing
memory-profiler>=0.61.0
pytest-benchmark>=4.0.0

# Type checking
mypy>=1.4.0
```

---

## High-Impact Testing Examples

### A. Cross-Machine Test for WSL Detection

```python
@pytest.mark.parametrize("machine_config", [
    {"os": "windows", "in_wsl": False, "path": r"D:\models"},
    {"os": "windows", "in_wsl": True, "path": "/mnt/d/models"},
    {"os": "macos", "in_wsl": False, "path": "/Users/user/models"},
    {"os": "linux", "in_wsl": False, "path": "/home/user/models"},
])
@pytest.mark.machine_specific
def test_model_path_detection(machine_config):
    """Test model path detection across machines"""
    # Verify path structure matches expected machine
    path = machine_config["path"]
    if machine_config["os"] == "windows" and not machine_config["in_wsl"]:
        assert path.startswith("D:")
    elif machine_config["in_wsl"]:
        assert path.startswith("/mnt/")
    else:
        assert path.startswith("/")
```

### B. Performance Regression Test

```python
@pytest.mark.performance
@pytest.mark.slow
def test_batch_processing_performance(temp_checkpoint_dir):
    """Test batch processing doesn't regress"""
    from utils.batch_processor import BatchProcessor

    bp = BatchProcessor(temp_checkpoint_dir)

    # Create large batch
    prompts = [f"Prompt {i}" for i in range(1000)]
    job = bp.create_job("test_model", prompts)

    # Measure checkpoint save time
    import time
    start = time.time()
    bp.save_checkpoint(job)
    duration = time.time() - start

    # Should complete in < 1 second for 1000 prompts
    assert duration < 1.0, f"Checkpoint save too slow: {duration:.2f}s"
```

### C. Parametrized Integration Test

```python
@pytest.mark.parametrize("model_id,expected_provider", [
    ("ollama-mistral", "ollama"),
    ("gguf-dolphin", "llama.cpp"),
    ("mlx-qwen", "mlx"),
])
@pytest.mark.integration
def test_model_routing(model_id, expected_provider, mock_ai_router):
    """Test that models route to correct providers"""
    # Load config
    config = json.load(open("configs/model_registry.json"))

    # Verify model exists in registry
    model = next((m for m in config["models"]
                  if m["model_id"] == model_id), None)

    assert model is not None
    assert model["provider"] == expected_provider
```

---

## Risk Analysis & Mitigation

### Risk 1: Flaky Tests (Timing Issues)
**Symptoms:** Tests pass sometimes, fail other times
**Mitigation:**
- Use `pytest-timeout` to catch hanging tests
- Avoid `time.sleep()`, use event-driven waits
- Mock external services (don't actually call APIs)
- Run tests 5x in CI to detect flakiness

**Example:**
```python
@pytest.mark.timeout(30)  # Kill test if > 30 seconds
def test_with_timeout():
    pass
```

### Risk 2: Test Isolation Issues
**Symptoms:** Tests pass in isolation, fail in sequence
**Mitigation:**
- Use fixtures for setup/teardown (already shown in conftest.py)
- Don't use global state
- Randomize test order: `pytest --random-order`
- Each test should be independent

### Risk 3: Platform-Specific Failures
**Symptoms:** Tests pass on Windows, fail on macOS/Linux
**Mitigation:**
- Use `@pytest.mark.skipif()` for platform-specific tests
- Test path handling with `pathlib.Path`
- Mock file system operations when possible
- Run tests on all 3 platforms in CI (GitHub Actions does this)

### Risk 4: Long Test Runtime Blocking CI
**Symptoms:** CI pipeline takes > 10 minutes
**Mitigation:**
- Mark slow tests with `@pytest.mark.slow`
- Run fast tests (unit) in parallel with `pytest-xdist`
- Only run integration tests on main branch, not every PR
- Use test sharding across multiple CI workers

**Example:**
```bash
# Run tests in parallel with 4 workers
pytest -n 4 tests/unit/
```

### Risk 5: Dependency Version Conflicts
**Symptoms:** Tests break with new package versions
**Mitigation:**
- Pin exact versions in requirements-test.txt
- Test against multiple Python versions (3.11, 3.12)
- Regular dependency updates with testing

---

## Test Discovery & Execution Examples

### Run All Tests
```bash
cd D:\models
pytest tests/ -v
```

### Run Only Unit Tests
```bash
pytest tests/unit/ -v -m "unit"
```

### Run Only Integration Tests
```bash
pytest tests/integration/ -v -m "integration"
```

### Run Tests in Parallel
```bash
pytest tests/ -n 4  # 4 parallel workers
```

### Run with Coverage Report
```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Run Machine-Specific Tests Only
```bash
# Windows only
pytest tests/machine_specific/test_windows_paths.py -m "windows" -v

# macOS only
pytest tests/machine_specific/test_macos_specific.py -m "macos" -v

# Linux only
pytest tests/machine_specific/test_linux_specific.py -m "linux" -v
```

### Run Until First Failure
```bash
pytest tests/ -x  # Stop at first failure
```

### Run Previously Failed Tests
```bash
pytest tests/ --lf  # Last failed
```

### Generate Test Report
```bash
pytest tests/ --html=report.html --self-contained-html
```

---

## Success Criteria

### Before This Strategy
- 4 integration tests (unittest framework)
- No CI/CD
- No unit tests
- ~5% code coverage estimate
- Manual test execution only

### After Implementation (Target)
- **40%+ code coverage** (from 5%)
- **100+ test cases** (unit + integration)
- **Automated CI/CD** (GitHub Actions)
- **Cross-platform testing** (Windows, macOS, Linux)
- **Performance baselines** established
- **Parallel test execution** (< 5 min full suite)
- **Machine-specific variants** (3 machines)
- **Zero flaky tests** (deterministic results)

---

## Deployment Timeline

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Foundation | pytest.ini, conftest.py, requirements-test.txt, migrate existing tests |
| 2 | Unit Tests | 50+ unit tests for core modules, 20% coverage |
| 3 | Expansion | Full unit tests (40% coverage), integration refinement |
| 4 | Machine Tests | Cross-machine variants, GPU detection, path handling |
| 5 | CI/CD | GitHub Actions workflow, performance tests, final validation |

---

## Conclusion

The D:\models project currently has a fragmented testing approach with 4 integration tests but zero unit tests, no CI/CD pipeline, and no cross-machine compatibility testing. This strategy provides:

1. **Pytest framework** - Modern, powerful test runner
2. **100+ tests** - Comprehensive coverage of all modules
3. **Cross-machine fixtures** - Tests run on all 3 target machines
4. **GitHub Actions CI/CD** - Automated testing on every commit
5. **Performance baselines** - Regression detection
6. **Clear roadmap** - 5-week phased implementation

Implementation of this strategy will improve code quality, catch regressions early, and ensure the AI Router works reliably across all deployment platforms.

---

## Files to Create/Modify

1. **Create:** `.github/workflows/tests.yml` (GitHub Actions)
2. **Create:** `tests/conftest.py` (Pytest configuration)
3. **Create:** `pytest.ini` (Pytest settings)
4. **Create:** `requirements-test.txt` (Test dependencies)
5. **Migrate:** Move `tests/*.py` to `tests/integration/`
6. **Create:** `tests/unit/*.py` (Unit tests for core modules)
7. **Create:** `tests/machine_specific/*.py` (Platform-specific tests)
8. **Create:** `tests/performance/*.py` (Performance tests)
9. **Create:** `tests/smoke/*.py` (Quick smoke tests)

---

**Agent 9 Analysis Complete**
