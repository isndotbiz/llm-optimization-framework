# AI Router Enhanced - Testing Quick Reference

## One-Line Commands

```bash
# Quick validation (30s)
python validate_installation.py

# Smoke test (2min)
python smoke_test.py

# Full integration tests (5-10min)
python test_integration.py

# Performance benchmarks
python benchmark_features.py

# Compatibility check
python test_compatibility.py

# Individual feature tests
python -m unittest tests.test_session_manager_integration
python -m unittest tests.test_template_manager_integration
python -m unittest tests.test_batch_processor_integration
python -m unittest tests.test_workflow_engine_integration
```

## Required Setup

```bash
# Install required dependency
pip install pyyaml

# Install all dependencies
pip install pyyaml jinja2 requests

# Optional dependencies
pip install tiktoken pandas matplotlib
```

## Test Files Location

```
D:\models\
├── test_integration.py          ← Master test suite
├── validate_installation.py     ← Quick validator
├── smoke_test.py                ← Fast test
├── benchmark_features.py        ← Performance
├── test_compatibility.py        ← Platform check
└── tests/                       ← Feature tests
    ├── test_session_manager_integration.py
    ├── test_template_manager_integration.py
    ├── test_batch_processor_integration.py
    └── test_workflow_engine_integration.py
```

## Results Files

```bash
test_results.json          # Integration test results
benchmark_results.json     # Performance benchmarks
test_*.db                  # Temp databases (auto-cleaned)
```

## Feature Coverage

| Feature | Status | Tests |
|---------|--------|-------|
| Session Manager | ✓ Ready | 11 |
| Template Manager | ⚠ Needs PyYAML | 12 |
| Context Manager | ✓ Ready | 8 |
| Response Processor | ✓ Ready | 7 |
| Model Selector | ✓ Ready | 6 |
| Model Comparison | ✓ Ready | 8 |
| Batch Processor | ✓ Ready | 11 |
| Analytics | ✓ Ready | 7 |
| Workflow Engine | ⚠ Needs PyYAML | 11 |

## Quick Troubleshooting

### PyYAML Error
```bash
pip install pyyaml
```

### Import Error
```bash
# Add to path
set PYTHONPATH=D:\models;%PYTHONPATH%
```

### Database Error
```bash
# Check schema exists
cat D:\models\schema.sql

# Remove old test databases
rm D:\models\test_*.db
```

## Expected Results

### Validation
- Passed: 24/24 checks
- Failed: 0
- Warnings: 2-4 (optional features)

### Integration Tests
- Total: 45+ tests
- Passed: 45
- Failed: 0
- Time: 5-10 minutes

### Benchmarks
- Session create: < 10ms
- Template render: < 1ms
- File load (1KB): < 1ms
- Database search: < 20ms

## Documentation

- `TESTING_GUIDE.md` - Complete testing guide
- `TEST_RESULTS_SUMMARY.md` - Detailed results
- `INTEGRATION_CHECKLIST.md` - Validation checklist
- `INTEGRATION_TEST_COMPLETE.md` - Summary report
- `TEST_QUICK_REFERENCE.md` - This file

## Support

Check documentation in order:
1. TEST_QUICK_REFERENCE.md (this file)
2. TESTING_GUIDE.md (detailed guide)
3. TEST_RESULTS_SUMMARY.md (results analysis)
4. INTEGRATION_CHECKLIST.md (step-by-step)
