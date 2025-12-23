#!/usr/bin/env python3
"""
Unit tests for SecurityValidator
"""

import sys
from pathlib import Path
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from security_validator import SecurityValidator


def test_validator():
    """Run basic validator tests"""
    validator = SecurityValidator()

    print("Testing SecurityValidator...")
    print("=" * 60)

    test_results = []

    # Test 1: Valid project name
    valid, error = validator.validate_project_name("my_project")
    test_results.append(("Valid project name", valid and error is None))
    print(f"[{'PASS' if valid else 'FAIL'}] Valid project name: my_project")

    # Test 2: Path traversal in project name
    valid, error = validator.validate_project_name("../../../etc")
    test_results.append(("Path traversal blocked", not valid))
    print(f"[{'PASS' if not valid else 'FAIL'}] Path traversal blocked: ../../../etc")

    # Test 3: Hidden file in project name
    valid, error = validator.validate_project_name(".hidden")
    test_results.append(("Hidden file blocked", not valid))
    print(f"[{'PASS' if not valid else 'FAIL'}] Hidden file blocked: .hidden")

    # Test 4: Invalid characters in project name
    valid, error = validator.validate_project_name("project@evil")
    test_results.append(("Invalid chars blocked", not valid))
    print(f"[{'PASS' if not valid else 'FAIL'}] Invalid chars blocked: project@evil")

    # Test 5: Valid query
    valid, error = validator.validate_query("test query")
    test_results.append(("Valid query", valid and error is None))
    print(f"[{'PASS' if valid else 'FAIL'}] Valid query: test query")

    # Test 6: Oversized query
    valid, error = validator.validate_query("x" * 600)
    test_results.append(("Oversized query blocked", not valid))
    print(f"[{'PASS' if not valid else 'FAIL'}] Oversized query blocked")

    # Test 7: Null query
    valid, error = validator.validate_query(None)
    test_results.append(("Null query blocked", not valid))
    print(f"[{'PASS' if not valid else 'FAIL'}] Null query blocked")

    # Test 8: Valid tags
    valid, error = validator.validate_tags(["tag1", "tag2"])
    test_results.append(("Valid tags", valid and error is None))
    print(f"[{'PASS' if valid else 'FAIL'}] Valid tags: ['tag1', 'tag2']")

    # Test 9: Invalid tags (too many)
    valid, error = validator.validate_tags(["tag"] * 100)
    test_results.append(("Too many tags blocked", not valid))
    print(f"[{'PASS' if not valid else 'FAIL'}] Too many tags blocked")

    # Test 10: Date validation
    valid, error = validator.validate_date_string("2025-01-15")
    test_results.append(("Valid date", valid and error is None))
    print(f"[{'PASS' if valid else 'FAIL'}] Valid date: 2025-01-15")

    # Test 11: Invalid date format
    valid, error = validator.validate_date_string("2025/01/15")
    test_results.append(("Invalid date format blocked", not valid))
    print(f"[{'PASS' if not valid else 'FAIL'}] Invalid date format blocked")

    # Test 12: Results size validation
    valid, error = validator.validate_results_size({"data": "small"})
    test_results.append(("Valid results size", valid and error is None))
    print(f"[{'PASS' if valid else 'FAIL'}] Valid results size")

    # Test 13: Oversized results
    valid, error = validator.validate_results_size({"data": "x" * (11 * 1024 * 1024)})
    test_results.append(("Oversized results blocked", not valid))
    print(f"[{'PASS' if not valid else 'FAIL'}] Oversized results blocked")

    # Test 14: Safe project path generation
    path = validator.get_safe_project_path("valid_project")
    test_results.append(("Safe path generated", path is not None))
    print(f"[{'PASS' if path else 'FAIL'}] Safe path generated: {path}")

    # Test 15: Invalid project path blocked
    path = validator.get_safe_project_path("../escape")
    test_results.append(("Invalid path blocked", path is None))
    print(f"[{'PASS' if path is None else 'FAIL'}] Invalid path blocked: ../escape")

    # Test 16: File path validation with temp dir
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
        tmp_path = tmp.name

    valid, error = validator.validate_file_path(tmp_path, allowed_base_dir=str(Path(tmp_path).parent))
    test_results.append(("Valid file path", valid and error is None))
    print(f"[{'PASS' if valid else 'FAIL'}] Valid file path")

    # Test 17: Path traversal in file path
    valid, error = validator.validate_file_path("/etc/passwd")
    test_results.append(("Path traversal in file path blocked", not valid))
    print(f"[{'PASS' if not valid else 'FAIL'}] Path traversal in file path blocked")

    # Summary
    print("=" * 60)
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("All tests PASSED!")
        return True
    else:
        print("Some tests FAILED:")
        for name, result in test_results:
            if not result:
                print(f"  - {name}")
        return False


if __name__ == '__main__':
    success = test_validator()
    sys.exit(0 if success else 1)
