# Testing Implementation Checklist

**Agent 9: Testing Strategy & CI/CD Expert**
**Last Updated:** December 22, 2025

---

## Phase 0: Validation (Immediate - 30 min)

- [ ] Download and review all created files
  - [ ] TESTING-STRATEGY-AND-CI-CD.md (comprehensive analysis)
  - [ ] TESTING-QUICK-START.md (quick reference)
  - [ ] TESTING-IMPLEMENTATION-SUMMARY.md (deliverables overview)
  - [ ] pytest.ini (global pytest config)
  - [ ] requirements-test.txt (dependencies)
  - [ ] tests/conftest.py (shared fixtures)
  - [ ] .github/workflows/tests.yml (CI/CD pipeline)
  - [ ] tests/unit/test_example_unit.py (example tests)

- [ ] Verify files are in correct locations
  ```
  D:\models\
  ├── pytest.ini
  ├── requirements-test.txt
  ├── TESTING-STRATEGY-AND-CI-CD.md
  ├── TESTING-QUICK-START.md
  ├── TESTING-IMPLEMENTATION-SUMMARY.md
  ├── TESTING-IMPLEMENTATION-CHECKLIST.md (this file)
  ├── tests/
  │   ├── conftest.py
  │   └── unit/
  │       └── test_example_unit.py
  └── .github/
      └── workflows/
          └── tests.yml
  ```

- [ ] Read TESTING-QUICK-START.md (5 minutes)

---

## Phase 1: Foundation (Week 1 - 2-3 hours)

### 1.1 Install Dependencies

- [ ] Install test framework packages
  ```bash
  cd D:\models
  pip install -r requirements-test.txt
  ```

- [ ] Verify pytest installation
  ```bash
  pytest --version
  # Should output: pytest X.X.X
  ```

- [ ] Verify pytest.ini is readable
  ```bash
  pytest --co -q
  # Should show test collection without errors
  ```

### 1.2 Explore Existing Tests

- [ ] List all existing test files
  ```bash
  pytest --collect-only tests/ -q
  ```

- [ ] Run existing integration tests with pytest
  ```bash
  pytest tests/ -v
  ```

- [ ] Record current test results
  - [ ] Number of tests passing: ____
  - [ ] Number of tests failing: ____
  - [ ] Total execution time: ____

### 1.3 Validate Conftest.py

- [ ] Check available fixtures
  ```bash
  pytest --fixtures -v | grep -E "^[a-z_]+"
  ```

- [ ] Count fixtures
  - [ ] Machine detection: ✓ (5 fixtures)
  - [ ] Temp directories: ✓ (5 fixtures)
  - [ ] Database: ✓ (3 fixtures)
  - [ ] Mocks: ✓ (3 fixtures)
  - [ ] Sample data: ✓ (4 fixtures)
  - [ ] Performance: ✓ (2 fixtures)

### 1.4 Run Example Tests

- [ ] Run example unit tests
  ```bash
  pytest tests/unit/test_example_unit.py -v
  ```

- [ ] Verify test output shows:
  - [ ] Test class structure visible
  - [ ] Multiple test methods executed
  - [ ] Fixtures being used
  - [ ] All tests passing

### 1.5 Generate Coverage Report

- [ ] Run tests with coverage
  ```bash
  pytest tests/ --cov=utils --cov-report=html
  ```

- [ ] Open coverage report
  ```bash
  # Windows: start htmlcov/index.html
  # macOS: open htmlcov/index.html
  # Linux: xdg-open htmlcov/index.html
  ```

- [ ] Record baseline coverage
  - [ ] Overall coverage: ____%
  - [ ] utils/ coverage: ____%

---

## Phase 2: Unit Tests (Week 1-2 - 4-6 hours)

### 2.1 Plan Unit Tests

- [ ] List all core modules needing unit tests
  ```python
  # Priority 1 (Critical)
  [ ] utils/session_manager.py
  [ ] utils/batch_processor.py
  [ ] utils/workflow_engine.py
  [ ] utils/template_manager.py

  # Priority 2 (Important)
  [ ] logging_config.py
  [ ] ai-router.py (core functions only)

  # Priority 3 (Nice to have)
  [ ] health_assessment.py
  [ ] Other utilities
  ```

### 2.2 Create Unit Test Files

For each module, create `tests/unit/test_<module_name>.py`:

- [ ] tests/unit/test_session_manager.py
  - [ ] Test SessionManager.__init__()
  - [ ] Test create_session()
  - [ ] Test get_session()
  - [ ] Test add_message()
  - [ ] Test delete_session()
  - [ ] Test search_messages()
  - [ ] Target: 15+ tests

- [ ] tests/unit/test_batch_processor.py
  - [ ] Test BatchProcessor.__init__()
  - [ ] Test create_job()
  - [ ] Test save_checkpoint()
  - [ ] Test load_checkpoint()
  - [ ] Test resume_job()
  - [ ] Test get_statistics()
  - [ ] Target: 15+ tests

- [ ] tests/unit/test_template_manager.py
  - [ ] Test PromptTemplate.__init__()
  - [ ] Test render()
  - [ ] Test variable_parsing()
  - [ ] Test default_values()
  - [ ] Target: 10+ tests

- [ ] tests/unit/test_workflow_engine.py
  - [ ] Test WorkflowEngine.__init__()
  - [ ] Test load_workflow()
  - [ ] Test execute_workflow()
  - [ ] Test step_dependencies()
  - [ ] Test error_handling()
  - [ ] Target: 15+ tests

- [ ] tests/unit/test_logging_config.py
  - [ ] Test setup_logging()
  - [ ] Test logger_creation()
  - [ ] Test log_levels()
  - [ ] Target: 8+ tests

### 2.3 Write Test Code

For each test file:
- [ ] Import necessary modules
- [ ] Create test class (e.g., `class TestSessionManager`)
- [ ] Add `@pytest.mark.unit` decorator to each test
- [ ] Use fixtures from conftest.py
- [ ] Mock external dependencies
- [ ] Assert expected behavior
- [ ] Clean up resources in tearDown

**Example structure:**
```python
import pytest
from utils.session_manager import SessionManager

class TestSessionManager:

    def setup_method(self):
        """Setup before each test"""
        self.sm = SessionManager(test_db_path)

    @pytest.mark.unit
    def test_create_session(self):
        """Test creating a session"""
        session_id = self.sm.create_session("test_model")
        assert session_id is not None
```

### 2.4 Run Unit Tests

- [ ] Run all unit tests
  ```bash
  pytest tests/unit/ -v -m unit
  ```

- [ ] Record results
  - [ ] Number of unit tests: ____
  - [ ] Pass rate: ____%
  - [ ] Execution time: ____ seconds

- [ ] Fix failing tests
  - [ ] Review error messages
  - [ ] Update test or code as needed
  - [ ] Re-run until all pass

### 2.5 Coverage Analysis

- [ ] Generate coverage report for unit tests
  ```bash
  pytest tests/unit/ --cov=utils --cov-report=html
  ```

- [ ] Check coverage by module
  - [ ] session_manager.py: ____%
  - [ ] batch_processor.py: ____%
  - [ ] template_manager.py: ____%
  - [ ] workflow_engine.py: ____%
  - [ ] Total utils/: ____%

- [ ] Target: 40%+ total coverage at end of week

---

## Phase 3: Machine-Specific Tests (Week 2-3 - 3-4 hours)

### 3.1 Create Test Files

- [ ] tests/machine_specific/test_windows_paths.py
  - [ ] Windows path format tests
  - [ ] Backslash handling
  - [ ] Drive letter handling
  - [ ] Mark: @pytest.mark.windows

- [ ] tests/machine_specific/test_wsl_compatibility.py
  - [ ] WSL detection tests
  - [ ] Mount point path handling (/mnt/d/)
  - [ ] Cross-platform path conversion
  - [ ] Mark: @pytest.mark.wsl

- [ ] tests/machine_specific/test_macos_specific.py
  - [ ] macOS path handling
  - [ ] MLX framework detection
  - [ ] M4 Pro specific tests
  - [ ] Mark: @pytest.mark.macos

- [ ] tests/machine_specific/test_linux_specific.py
  - [ ] Linux path handling
  - [ ] /proc filesystem access
  - [ ] GPU detection (CUDA)
  - [ ] Mark: @pytest.mark.linux

- [ ] tests/machine_specific/test_gpu_detection.py
  - [ ] CUDA availability check
  - [ ] MLX availability check
  - [ ] GPU memory reporting
  - [ ] Mark: @pytest.mark.gpu

### 3.2 Implement Machine Detection Tests

Each test should:
- [ ] Use machine detection fixtures (machine_type, is_wsl, is_macos, etc.)
- [ ] Skip if not on correct machine
- [ ] Test path handling specific to machine
- [ ] Verify device detection

**Example:**
```python
@pytest.mark.windows
@pytest.mark.machine_specific
def test_windows_path_conversion(self):
    """Test Windows path handling"""
    path = Path("D:\\models\\file.gguf")
    assert path.drive == "D:"
```

### 3.3 Run Machine-Specific Tests

- [ ] Run all machine-specific tests
  ```bash
  pytest tests/machine_specific/ -v
  ```

- [ ] Run specific machine tests
  ```bash
  # Windows
  pytest tests/machine_specific/ -v -m windows

  # WSL
  pytest tests/machine_specific/ -v -m wsl

  # macOS
  pytest tests/machine_specific/ -v -m macos

  # Linux
  pytest tests/machine_specific/ -v -m linux
  ```

- [ ] Record results
  - [ ] Tests on Windows: _____ pass
  - [ ] Tests on WSL: _____ pass
  - [ ] Tests on macOS: _____ pass
  - [ ] Tests on Linux: _____ pass

---

## Phase 4: Integration Tests (Week 3 - 2-3 hours)

### 4.1 Migrate Existing Tests

- [ ] Move existing integration tests
  ```bash
  mv tests/test_*.py tests/integration/
  ```

- [ ] Update imports in migrated tests
  - [ ] Remove manual sys.path.insert lines
  - [ ] Remove Path manipulations
  - [ ] Update to use conftest.py fixtures

### 4.2 Create End-to-End Test

- [ ] tests/integration/test_end_to_end.py
  - [ ] Complete workflow execution test
  - [ ] Session creation → execution → cleanup
  - [ ] Multiple modules working together
  - [ ] 5+ end-to-end scenarios

### 4.3 Run Integration Tests

- [ ] Run all integration tests
  ```bash
  pytest tests/integration/ -v -m integration
  ```

- [ ] Record results
  - [ ] Number of integration tests: ____
  - [ ] Pass rate: ____%
  - [ ] Total execution time: ____ seconds

---

## Phase 5: Performance Tests (Week 4 - 2-3 hours)

### 5.1 Create Performance Test Files

- [ ] tests/performance/test_batch_performance.py
  - [ ] Large batch handling (1000+ prompts)
  - [ ] Performance regression detection
  - [ ] Memory usage tracking
  - [ ] Mark: @pytest.mark.performance, @pytest.mark.slow

- [ ] tests/performance/test_session_memory.py
  - [ ] Memory leak detection
  - [ ] Long-running session tests
  - [ ] Mark: @pytest.mark.performance

- [ ] tests/performance/test_model_loading_speed.py
  - [ ] Model loading benchmarks
  - [ ] Speed regression detection
  - [ ] Mark: @pytest.mark.performance

### 5.2 Implement Performance Baselines

Each performance test should:
- [ ] Record baseline metrics (first run)
- [ ] Compare against baselines on subsequent runs
- [ ] Use `track_time` and `track_memory` fixtures
- [ ] Alert if performance degrades > 10%

**Example:**
```python
@pytest.mark.performance
def test_batch_performance(track_time):
    """Batch processing should complete in < 1 second"""
    with track_time:
        process_batch(1000)

    assert track_time.duration < 1.0  # Baseline
```

### 5.3 Run Performance Tests

- [ ] Run performance tests
  ```bash
  pytest tests/performance/ -v -m performance
  ```

- [ ] Record baseline metrics
  - [ ] Batch processing speed: ____ seconds
  - [ ] Session memory usage: ____ MB
  - [ ] Model loading time: ____ seconds

---

## Phase 6: CI/CD Integration (Week 4-5 - 2-3 hours)

### 6.1 GitHub Setup

- [ ] Verify .github/workflows/tests.yml exists
- [ ] Push all changes to GitHub repository
  ```bash
  git add .
  git commit -m "Add comprehensive testing infrastructure"
  git push origin main
  ```

### 6.2 Verify CI/CD Pipeline

- [ ] Visit GitHub repository Actions page
- [ ] Verify tests.yml workflow appears
- [ ] Wait for initial run to complete
- [ ] Check results:
  - [ ] Smoke tests: ✓ Passed
  - [ ] Unit tests: ✓ Passed
  - [ ] Integration tests: ✓ Passed
  - [ ] Machine-specific tests: ✓ Passed
  - [ ] Code quality: ✓ Passed
  - [ ] Security scan: ✓ Passed

### 6.3 Setup Code Coverage

- [ ] Create Codecov account (codecov.io)
- [ ] Link GitHub repository
- [ ] Verify coverage reports upload
- [ ] Check coverage badge generation

### 6.4 Configure Branch Protection

- [ ] Go to repository settings
- [ ] Find "Branches" section
- [ ] Click "Add rule" for main branch
- [ ] Enable:
  - [ ] Require status checks to pass before merging
  - [ ] Select: smoke-tests, unit-tests, integration-tests
  - [ ] Require branches to be up to date before merging

---

## Phase 7: Documentation & Cleanup (Week 5 - 1-2 hours)

### 7.1 Update README

- [ ] Add Testing section to README.md
  ```markdown
  ## Testing

  Run all tests:
  ```bash
  pytest tests/ -v
  ```

  See [TESTING-QUICK-START.md](TESTING-QUICK-START.md) for details.
  ```

- [ ] Add CI/CD badge
  ```markdown
  ![Tests](https://github.com/USER/REPO/actions/workflows/tests.yml/badge.svg)
  [![Codecov](https://codecov.io/gh/USER/REPO/badge.svg)](https://codecov.io/gh/USER/REPO)
  ```

### 7.2 Archive Old Tests

- [ ] Review archive/old-tests/ directory
- [ ] Migrate any tests not yet covered
- [ ] Mark as deprecated in comments
- [ ] Keep for reference only

### 7.3 Document Test Patterns

- [ ] Create tests/TESTING-PATTERNS.md
  - [ ] Document common test patterns
  - [ ] Show fixture usage examples
  - [ ] Explain parametrization
  - [ ] Demonstrate mocking strategies

### 7.4 Create Test Maintenance Guide

- [ ] Document how to:
  - [ ] Add new unit tests
  - [ ] Update fixtures
  - [ ] Run tests locally
  - [ ] Debug failing tests
  - [ ] Measure coverage

---

## Phase 8: Final Validation (Week 5 - 1 hour)

### 8.1 Coverage Target Validation

- [ ] Generate final coverage report
  ```bash
  pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
  ```

- [ ] Check final coverage metrics
  - [ ] Overall coverage: Target 40%, Actual ____%
  - [ ] utils/ coverage: Target 60%, Actual ____%
  - [ ] Core modules: Target 80%, Actual ____%

### 8.2 Test Count Validation

- [ ] Count all tests by type
  ```bash
  pytest --collect-only -q tests/
  ```

  - [ ] Smoke tests: _____ (target: 5+)
  - [ ] Unit tests: _____ (target: 50+)
  - [ ] Integration tests: _____ (target: 20+)
  - [ ] Machine-specific tests: _____ (target: 15+)
  - [ ] Performance tests: _____ (target: 10+)
  - [ ] **Total: _____ (target: 100+)**

### 8.3 Execution Speed Validation

- [ ] Measure full test execution
  ```bash
  time pytest tests/ -v --tb=short
  ```

  - [ ] Sequential execution: Target < 20 min, Actual ____ min

- [ ] Measure parallel execution
  ```bash
  time pytest tests/ -n 4 -v
  ```

  - [ ] Parallel execution (4 workers): Target < 5 min, Actual ____ min

### 8.4 CI/CD Validation

- [ ] Verify GitHub Actions workflow
  - [ ] Last run status: ✓ All passing
  - [ ] Execution time: ____ minutes
  - [ ] Coverage report generated: ✓ Yes
  - [ ] Code quality checks: ✓ Passed
  - [ ] Security scan: ✓ No vulnerabilities

### 8.5 Cross-Platform Validation

- [ ] Verify tests run on all platforms
  - [ ] Ubuntu (Linux): ✓ All tests pass
  - [ ] Windows: ✓ All tests pass
  - [ ] macOS: ✓ All tests pass
  - [ ] Python 3.11: ✓ All tests pass
  - [ ] Python 3.12: ✓ All tests pass

---

## Success Metrics (Target Results)

### Code Coverage
- [x] Baseline: ~5%
- [ ] Target: 40%+
- [ ] Critical modules (Session, Batch, Workflow): 80%+

### Test Count
- [x] Baseline: 4 integration tests
- [ ] Target: 100+ total tests
  - [ ] 50+ unit tests
  - [ ] 20+ integration tests
  - [ ] 15+ machine-specific tests
  - [ ] 10+ performance tests

### Execution Speed
- [ ] Sequential: < 20 minutes
- [ ] Parallel (4 workers): < 5 minutes
- [ ] Smoke tests: < 1 minute

### Quality Metrics
- [ ] 0 flaky tests (deterministic)
- [ ] 0 platform-specific failures
- [ ] 100% CI/CD pass rate
- [ ] 0 security vulnerabilities

### Machine Compatibility
- [ ] Tests pass on Windows
- [ ] Tests pass on WSL
- [ ] Tests pass on macOS
- [ ] Tests pass on Linux
- [ ] GPU detection works
- [ ] Path handling verified

---

## Rollback Plan (If Needed)

If implementation needs to pause:

1. **Save current state**
   ```bash
   git stash
   git tag testing-phase-N
   ```

2. **Resume later**
   ```bash
   git tag -l testing-phase-*
   git checkout testing-phase-N
   git stash pop
   ```

3. **Continue from next phase**
   - Reference this checklist
   - Check git tags for saved states

---

## Sign-Off

- [ ] All phases complete
- [ ] Coverage target achieved (40%+)
- [ ] 100+ tests passing
- [ ] CI/CD pipeline operational
- [ ] Documentation complete
- [ ] Team trained on testing approach
- [ ] Ready for production deployment

---

**Implementation Start Date:** _______________
**Expected Completion Date:** _______________
**Actual Completion Date:** _______________

**Sign-Off By:** _______________
**Date:** _______________

---

## Questions & Support

For questions about:
- **Quick usage:** See TESTING-QUICK-START.md
- **Strategy:** See TESTING-STRATEGY-AND-CI-CD.md
- **Pytest basics:** Run `pytest --help`
- **Available fixtures:** Run `pytest --fixtures`
- **Test patterns:** See tests/unit/test_example_unit.py

---

**Created by Agent 9: Testing Strategy & CI/CD Expert**
**December 22, 2025**
