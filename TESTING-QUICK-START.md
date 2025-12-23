# Testing Quick Start Guide

## 5-Minute Setup

### Step 1: Install Pytest Framework

```bash
cd D:\models
pip install -r requirements-test.txt
```

### Step 2: Verify Installation

```bash
pytest --version
# Output: pytest X.X.X
```

### Step 3: Run Quick Smoke Test

```bash
pytest tests/smoke/ -v
```

**Expected Output:**
```
tests/smoke/test_imports.py::test_import_utils PASSED
tests/smoke/test_basic_initialization.py::test_sessionmanager_init PASSED
...
```

---

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Unit Tests Only (Fast)
```bash
pytest tests/unit/ -v -m unit
```

### Integration Tests (Medium)
```bash
pytest tests/integration/ -v -m integration
```

### Machine-Specific Tests
```bash
# Run only tests for current machine
pytest tests/machine_specific/ -v
```

### With Coverage Report
```bash
pytest tests/ -v --cov=utils --cov-report=html
# View report in browser: htmlcov/index.html
```

### Parallel Execution (4 workers)
```bash
pytest tests/ -n 4
```

### Stop at First Failure
```bash
pytest tests/ -x
```

### Re-run Failed Tests
```bash
pytest tests/ --lf
```

---

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures (run: pytest --fixtures)
├── smoke/                   # Basic smoke tests (< 1 min)
├── unit/                    # Unit tests (< 5 min)
├── integration/             # Integration tests (< 10 min)
├── machine_specific/        # Platform-specific tests
└── performance/             # Slow performance tests
```

---

## Create Your First Unit Test

Create `tests/unit/test_my_module.py`:

```python
import pytest

@pytest.mark.unit
def test_example(mock_ai_router):
    """Test example function"""
    # Use fixture mock_ai_router
    result = mock_ai_router.execute_prompt("test", "Hello")
    assert result == "Mock response from AI Router"
```

Run it:
```bash
pytest tests/unit/test_my_module.py -v
```

---

## Test Fixtures (Available Globally)

All fixtures are defined in `conftest.py`:

### Machine Detection
```python
def test_machine(machine_type, is_wsl, is_macos, is_windows, is_linux):
    if is_wsl:
        # WSL-specific logic
        pass
```

### Database
```python
def test_with_db(test_db_initialized):
    # Use initialized database
    pass
```

### Mocking
```python
def test_with_mocks(mock_ai_router, mock_logger, mock_model_config):
    # Use mocks instead of real implementations
    pass
```

### Temporary Directories
```python
def test_temp_files(temp_checkpoint_dir, temp_workflows_dir):
    # Create files in temporary directories (auto-cleaned)
    pass
```

### Sample Data
```python
def test_with_data(sample_prompts, sample_workflow_yaml, batch_job_samples):
    # Use predefined test data
    pass
```

### Performance Tracking
```python
def test_performance(track_time, track_memory):
    with track_time:
        # Code to measure
        pass
    print(track_time)  # Duration: X.XXXs
```

---

## Run Tests from Different Locations

### From Project Root
```bash
cd D:\models
pytest tests/
```

### From Specific Test Directory
```bash
cd D:\models\tests
pytest -v
```

### From Any Directory
```bash
pytest D:\models\tests\ -v
```

---

## Common Pytest Commands

| Command | Purpose |
|---------|---------|
| `pytest` | Run all tests |
| `pytest tests/unit/` | Run specific directory |
| `pytest test_file.py::test_func` | Run specific test |
| `pytest -v` | Verbose output |
| `pytest -x` | Stop at first failure |
| `pytest -n 4` | Parallel (4 workers) |
| `pytest --co` | Collect tests (don't run) |
| `pytest --co -q` | Quiet collection |
| `pytest -m unit` | Run tests with 'unit' marker |
| `pytest -m "not slow"` | Exclude slow tests |
| `pytest --lf` | Last failed |
| `pytest --ff` | Failed first |
| `pytest --fixtures` | Show available fixtures |
| `pytest --help` | Help |

---

## Debugging Tests

### Print Debug Info
```python
def test_debug(caplog):
    """caplog fixture captures logging output"""
    import logging
    logging.debug("Debug message")
    assert "Debug message" in caplog.text
```

### Use Python Debugger
```python
def test_with_debugger():
    import pdb; pdb.set_trace()  # Breakpoint
    # Code here
```

### See Test Output
```bash
pytest tests/ -v -s  # -s shows print() output
```

### See Fixture Values
```bash
pytest --fixtures -v  # Show all available fixtures
```

---

## CI/CD Pipeline Status

GitHub Actions workflows are in `.github/workflows/`:

1. **tests.yml** - Main testing pipeline
   - Smoke tests: Very fast (5 min)
   - Unit tests: Fast (15 min)
   - Integration tests: Medium (30 min)
   - Machine-specific: 20 min
   - Code quality: 10 min
   - Security: 10 min

### Check Pipeline Status
Visit: `https://github.com/YOUR-REPO/actions`

---

## Troubleshooting

### "pytest not found"
```bash
pip install pytest
pip install -r requirements-test.txt
```

### "Module not found" Error
```bash
# Check conftest.py adds project root to path
pytest tests/ -v  # Should work from any directory
```

### "Database locked" Error
```bash
# Fixtures cleanup automatically, but if stuck:
rm -rf test_*.db  # Remove test databases
pytest tests/
```

### Test Hangs / Times Out
```bash
# Default timeout is 300 seconds
pytest tests/ --timeout=60  # 60 second timeout
```

### Memory Issues
```bash
# Run tests sequentially instead of parallel
pytest tests/ -n 0  # No parallelization
```

---

## Next Steps

1. **Install test dependencies:** `pip install -r requirements-test.txt`
2. **Run smoke tests:** `pytest tests/smoke/ -v`
3. **Explore fixtures:** `pytest --fixtures`
4. **Write first unit test:** Create `tests/unit/test_my_code.py`
5. **Monitor CI/CD:** Check `.github/workflows/tests.yml` status

---

## Additional Resources

- pytest documentation: https://docs.pytest.org/
- Fixtures guide: https://docs.pytest.org/how-to/fixtures.html
- Parametrization: https://docs.pytest.org/parametrize.html
- Markers: https://docs.pytest.org/markers.html
- Coverage: https://coverage.readthedocs.io/

---

## Example Test Session

```bash
# 1. Run all tests
$ pytest tests/ -v --cov=utils --cov-report=term-missing

# 2. Output shows:
#    - 39 passed in 2.34s
#    - Coverage: 45% (utils module)
#    - Report in htmlcov/index.html

# 3. View coverage report
$ open htmlcov/index.html

# 4. Run only fast tests
$ pytest tests/unit/ tests/smoke/ -v

# 5. Debug failed test
$ pytest tests/unit/test_foo.py::test_function -vvs

# 6. Run in parallel
$ pytest tests/ -n 4 -v

# 7. Check for regressions
$ pytest tests/ -m "not slow" -v
```

---

## Support

For issues or questions:
1. Check `conftest.py` for available fixtures
2. Review test examples in `tests/`
3. Check pytest documentation
4. Run `pytest --help` for command-line options

Happy testing!
