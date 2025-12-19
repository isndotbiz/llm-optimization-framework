# AI Router Enhanced - Testing Guide

Complete guide for testing all 9 implemented features.

## Test Files Created

### Master Test Suite
- `test_integration.py` - Comprehensive integration test suite
- `validate_installation.py` - Quick installation validation
- `smoke_test.py` - 2-minute smoke test (no model execution)
- `benchmark_features.py` - Performance benchmarking
- `test_compatibility.py` - Cross-platform compatibility tests

### Feature-Specific Tests (tests/ directory)
- `tests/test_session_manager_integration.py` - Session management tests
- `tests/test_template_manager_integration.py` - Template system tests
- `tests/test_batch_processor_integration.py` - Batch processing tests
- `tests/test_workflow_engine_integration.py` - Workflow engine tests

## Quick Start

### 1. Quick Validation (30 seconds)
```bash
python validate_installation.py
```
Checks that all components are installed correctly.

### 2. Smoke Test (2 minutes)
```bash
python smoke_test.py
```
Tests basic functionality without executing models.

### 3. Full Integration Tests (5-10 minutes)
```bash
python test_integration.py
```
Comprehensive testing of all features.

### 4. Performance Benchmarks
```bash
python benchmark_features.py
```
Measures execution time for each feature.

### 5. Compatibility Tests
```bash
python test_compatibility.py
```
Tests cross-platform compatibility.

## Running Individual Feature Tests

```bash
# Session Manager
python -m unittest tests.test_session_manager_integration

# Template Manager
python -m unittest tests.test_template_manager_integration

# Batch Processor
python -m unittest tests.test_batch_processor_integration

# Workflow Engine
python -m unittest tests.test_workflow_engine_integration
```

## Test Coverage

### Category 1: Core Infrastructure
- ✓ Session Manager (database, CRUD, search)
- ✓ Response Capture (formatting, export)

### Category 2: Independent Features
- ✓ Prompt Templates (loading, rendering, variables)
- ✓ Context Management (file loading, token estimation)
- ✓ Response Processing (JSON/code extraction)
- ✓ Model Selector (capability matching)

### Category 3: Dependent Features
- ✓ Model Comparison (A/B testing, results storage)
- ✓ Batch Processing (job creation, checkpointing)
- ✓ Analytics (usage stats, model performance)

### Category 4: Advanced Features
- ✓ Workflows (multi-step, variable passing, dependencies)

### Category 5: Integration Tests
- ✓ Template + Context integration
- ✓ Session + Analytics integration
- ✓ Batch + Templates integration
- ✓ Workflow + Session integration

## Test Results

Results are saved to:
- `test_results.json` - Integration test results
- `benchmark_results.json` - Performance benchmarks

## What Each Test Validates

### validate_installation.py
- All required files exist
- Modules can be imported
- Database initialization works
- Dependencies are installed
- Directory structure is correct

### smoke_test.py
- Module imports work
- Database creation works
- Template loading works
- Context manager initializes
- Batch processor initializes
- Workflow engine initializes
- Analytics initializes
- Model comparison initializes
- Response processor initializes

### test_integration.py
**Session Manager:**
- Module import
- Database creation
- CRUD operations
- Search functionality
- Export features
- Session statistics

**Template Manager:**
- Template loading from YAML
- Variable substitution
- System and user prompts
- Category filtering
- Metadata extraction

**Context Manager:**
- File loading
- Token estimation
- Multi-file context building
- Context truncation

**Response Processor:**
- JSON extraction
- Code block extraction
- Markdown formatting

**Model Selector:**
- Capability matching
- Model recommendations

**Model Comparison:**
- Comparison creation
- Result storage
- Multi-model testing

**Batch Processor:**
- Job creation
- Checkpoint save/load
- Progress tracking
- Error handling

**Analytics:**
- Usage statistics
- Model performance metrics
- Token usage tracking

**Workflows:**
- Workflow loading
- Variable passing
- Step dependencies
- Multi-step execution

**Integration Tests:**
- Templates with context
- Sessions with analytics
- Batch with templates
- Workflows with sessions

### benchmark_features.py
**Performance Metrics:**
- Session creation speed
- Message insertion speed
- Search performance
- Template loading time
- Template rendering time
- File loading speed (various sizes)
- Token estimation speed
- Batch job creation
- Checkpoint operations
- Analytics query performance

### test_compatibility.py
**Environment Checks:**
- Python version (3.8+)
- Core dependencies
- Optional dependencies
- Windows compatibility
- Linux/WSL compatibility
- File system operations
- Module import compatibility

## Expected Results

### Success Criteria
All tests should pass with:
- ✓ 0 failed tests in integration suite
- ✓ All validations pass in installation check
- ✓ All smoke tests pass
- ✓ Benchmarks complete without errors
- ✓ Compatibility checks pass for your environment

### Common Issues

**Missing Dependencies:**
```bash
pip install pyyaml jinja2 requests
```

**Database Errors:**
- Ensure `schema.sql` exists in D:\models\
- Check file permissions

**Import Errors:**
- Verify all feature files exist
- Check Python path configuration

**Windows Path Issues:**
- Use absolute paths (D:\models\...)
- Ensure backslashes are escaped in strings

## Test Maintenance

### Adding New Tests
1. Create test file in `tests/` directory
2. Inherit from `unittest.TestCase`
3. Add setUp() and tearDown() methods
4. Write test methods (must start with `test_`)
5. Update test_integration.py if needed

### Test Data Cleanup
All tests automatically clean up:
- Test databases (test_*.db)
- Test directories (test_*)
- Temporary files

### Continuous Testing
Run before:
- Committing changes
- Releasing new features
- Deploying to production
- After dependency updates

## Integration Checklist

- [ ] All 9 feature modules exist
- [ ] All modules can be imported
- [ ] Database schema exists
- [ ] Core dependencies installed
- [ ] Installation validation passes
- [ ] Smoke test passes
- [ ] Integration tests pass
- [ ] Benchmarks run successfully
- [ ] Compatibility tests pass
- [ ] No test data left behind

## Troubleshooting

### Tests Won't Run
```bash
# Check Python version
python --version

# Check module imports
python -c "import sys; sys.path.insert(0, 'D:\\models'); import session_manager"

# Verify test files exist
ls D:\models\test*.py
ls D:\models\tests\
```

### Database Errors
```bash
# Check schema exists
cat D:\models\schema.sql

# Remove test databases
rm D:\models\test_*.db
```

### Import Errors
```bash
# Add to Python path
set PYTHONPATH=D:\models;%PYTHONPATH%

# Or in script
import sys
sys.path.insert(0, 'D:\\models')
```

## Performance Expectations

**Typical Benchmark Results:**
- Session creation: < 10ms
- Message insertion: < 5ms
- Template rendering: < 1ms
- File loading (1KB): < 1ms
- Database search: < 20ms

## Next Steps

After all tests pass:
1. Review test_results.json for detailed results
2. Check benchmark_results.json for performance metrics
3. Address any warnings from compatibility tests
4. Proceed with feature usage or deployment
5. Set up automated testing (CI/CD)

## Contact & Support

For issues with tests:
1. Check this guide for troubleshooting
2. Review test output for specific errors
3. Verify all prerequisites are met
4. Check file permissions and paths
