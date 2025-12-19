#!/usr/bin/env python3
"""
Simple validation test for workflow YAML files
Tests YAML syntax without requiring PyYAML to be installed
"""

from pathlib import Path
import json

def validate_yaml_syntax(file_path):
    """Basic YAML validation by checking common syntax patterns"""
    errors = []

    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Check for basic YAML structure
        has_id = False
        has_name = False
        has_steps = False
        in_steps = False
        step_count = 0

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check for required fields
            if stripped.startswith('id:'):
                has_id = True
            elif stripped.startswith('name:'):
                has_name = True
            elif stripped.startswith('steps:'):
                has_steps = True
                in_steps = True

            # Count steps
            if in_steps and stripped.startswith('- name:'):
                step_count += 1

            # Check for common YAML errors
            if stripped.startswith('-') and not (stripped.startswith('- ') or stripped.startswith('-  ')):
                errors.append(f"Line {i}: List items should have space after '-'")

            # Check for tabs (YAML uses spaces)
            if '\t' in line and not line.strip().startswith('#'):
                errors.append(f"Line {i}: YAML does not allow tabs, use spaces")

        if not has_id:
            errors.append("Missing required field: id")
        if not has_name:
            errors.append("Missing required field: name")
        if not has_steps:
            errors.append("Missing required field: steps")

        print(f"\n{'='*60}")
        print(f"Validating: {file_path.name}")
        print(f"{'='*60}")

        if errors:
            print(f"X Validation FAILED - {len(errors)} error(s) found:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"+ Basic syntax validation PASSED")
            print(f"  - Has ID: {has_id}")
            print(f"  - Has Name: {has_name}")
            print(f"  - Has Steps: {has_steps}")
            print(f"  - Step Count: {step_count}")

        return len(errors) == 0

    except Exception as e:
        print(f"X Error reading file: {e}")
        return False


def main():
    """Validate all workflow YAML files"""
    workflows_dir = Path("D:/models/workflows")

    if not workflows_dir.exists():
        print(f"Error: Workflows directory not found: {workflows_dir}")
        return

    yaml_files = list(workflows_dir.glob("*.yaml"))

    if not yaml_files:
        print(f"No workflow YAML files found in {workflows_dir}")
        return

    print(f"\nFound {len(yaml_files)} workflow file(s) to validate\n")

    results = {}
    for yaml_file in yaml_files:
        is_valid = validate_yaml_syntax(yaml_file)
        results[yaml_file.name] = is_valid

    # Summary
    print(f"\n{'='*60}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*60}")

    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed

    print(f"Total files: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print(f"\n+ All workflow files passed basic validation!")
    else:
        print(f"\nX {failed} file(s) need attention")

    # List files
    print(f"\nWorkflow files:")
    for filename, is_valid in results.items():
        status = "+" if is_valid else "X"
        print(f"  {status} {filename}")


if __name__ == "__main__":
    main()
