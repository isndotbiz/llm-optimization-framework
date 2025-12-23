#!/usr/bin/env python3
"""
Workflow Validator - Enhanced YAML validation with helpful error messages
Validates workflow structure and provides actionable feedback instead of generic errors
"""

from typing import Dict, List, Tuple, Any
from pathlib import Path
import yaml
import re


class WorkflowValidator:
    """Validates workflow YAML structure with detailed error reporting"""

    # Valid step types and their required fields
    STEP_TYPES = {
        'prompt': {
            'required': ['prompt'],
            'optional': ['model', 'output_var', 'on_error', 'timeout', 'retry'],
            'description': 'Execute a prompt against an AI model'
        },
        'template': {
            'required': ['template_id'],
            'optional': ['variables', 'model', 'output_var', 'on_error', 'timeout', 'retry'],
            'description': 'Execute using a prompt template'
        },
        'conditional': {
            'required': ['condition', 'then'],
            'optional': ['else'],
            'description': 'Branch based on condition evaluation'
        },
        'loop': {
            'required': ['items_var', 'body'],
            'optional': ['loop_var'],
            'description': 'Iterate over a list of items'
        },
        'extract': {
            'required': ['from_step'],
            'optional': ['pattern', 'output_var'],
            'description': 'Extract data from previous step result'
        },
        'sleep': {
            'required': [],
            'optional': ['duration'],
            'description': 'Pause execution for specified duration (seconds)'
        }
    }

    # Timeout constraints
    TIMEOUT_MIN = 1
    TIMEOUT_MAX = 3600

    # Retry constraints
    RETRY_BACKOFF_TYPES = ['exponential', 'linear', 'fixed']
    RETRY_MIN_ATTEMPTS = 1
    RETRY_MAX_ATTEMPTS = 10

    @staticmethod
    def validate_file(workflow_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate workflow YAML file

        Args:
            workflow_path: Path to workflow YAML file

        Returns:
            (is_valid, list_of_error_messages)
        """
        errors = []

        # Check file exists
        if not workflow_path.exists():
            return False, [f"Workflow file not found: {workflow_path}"]

        # Parse YAML
        try:
            data = yaml.safe_load(workflow_path.read_text(encoding='utf-8'))
        except yaml.YAMLError as e:
            return False, [f"Invalid YAML syntax: {e}"]
        except Exception as e:
            return False, [f"Failed to read workflow file: {e}"]

        if data is None:
            return False, ["Workflow file is empty"]

        # Validate structure
        errors.extend(WorkflowValidator.validate_structure(data))

        return len(errors) == 0, errors

    @staticmethod
    def validate_structure(data: Dict) -> List[str]:
        """
        Validate workflow data structure

        Args:
            data: Parsed workflow dictionary

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Validate top-level structure
        if not isinstance(data, dict):
            errors.append("Workflow must be a YAML dictionary (key: value pairs)")
            return errors

        # Check for steps
        if 'steps' not in data:
            errors.append("Missing required field 'steps' at root level")
            return errors

        if not isinstance(data['steps'], list):
            errors.append("Field 'steps' must be a list (use - for each step)")
            return errors

        if not data['steps']:
            errors.append("Field 'steps' cannot be empty - at least one step required")
            return errors

        # Validate workflow metadata (optional)
        if 'id' in data and not isinstance(data['id'], str):
            errors.append("Field 'id' must be a string")

        if 'name' in data and not isinstance(data['name'], str):
            errors.append("Field 'name' must be a string")

        if 'description' in data and not isinstance(data['description'], str):
            errors.append("Field 'description' must be a string")

        if 'variables' in data:
            if not isinstance(data['variables'], dict):
                errors.append("Field 'variables' must be a dictionary")

        # Validate steps
        step_names = set()
        errors.extend(
            WorkflowValidator._validate_steps(data['steps'], step_names)
        )

        return errors

    @staticmethod
    def _validate_steps(steps: List, step_names: set) -> List[str]:
        """Validate all steps in the workflow"""
        errors = []

        for step_idx, step in enumerate(steps):
            step_num = step_idx + 1

            if not isinstance(step, dict):
                errors.append(f"Step {step_num}: Step must be a dictionary (use 'key: value' format)")
                continue

            # Validate required fields
            if 'name' not in step:
                errors.append(f"Step {step_num}: Missing required field 'name'")
                continue

            step_name = step['name']

            if not isinstance(step_name, str):
                errors.append(f"Step {step_num}: Field 'name' must be a string, got {type(step_name).__name__}")
                continue

            # Check for duplicate names
            if step_name in step_names:
                errors.append(f"Step {step_num} ({step_name}): Duplicate step name. Step names must be unique.")
                continue

            step_names.add(step_name)

            # Validate type
            if 'type' not in step:
                errors.append(f"Step {step_num} ({step_name}): Missing required field 'type'")
                continue

            step_type = step['type']

            if step_type not in WorkflowValidator.STEP_TYPES:
                valid_types = ', '.join(WorkflowValidator.STEP_TYPES.keys())
                errors.append(
                    f"Step {step_num} ({step_name}): Invalid type '{step_type}'. "
                    f"Valid types are: {valid_types}"
                )
                continue

            # Validate step-specific fields
            errors.extend(
                WorkflowValidator._validate_step_fields(step, step_name, step_type)
            )

            # Validate timeout (if present)
            if 'timeout' in step:
                timeout_errors = WorkflowValidator._validate_timeout(step['timeout'], step_name)
                errors.extend(timeout_errors)

            # Validate retry (if present)
            if 'retry' in step:
                retry_errors = WorkflowValidator._validate_retry(step['retry'], step_name)
                errors.extend(retry_errors)

            # Validate dependencies (if present)
            if 'depends_on' in step:
                if not isinstance(step['depends_on'], list):
                    errors.append(
                        f"Step {step_name}: Field 'depends_on' must be a list of step names"
                    )

            # Validate condition syntax (for conditional steps)
            if step_type == 'conditional' and 'condition' in step:
                condition_errors = WorkflowValidator._validate_condition(
                    step['condition'], step_name
                )
                errors.extend(condition_errors)

        return errors

    @staticmethod
    def _validate_step_fields(step: Dict, step_name: str, step_type: str) -> List[str]:
        """Validate step-specific required and optional fields"""
        errors = []
        step_info = WorkflowValidator.STEP_TYPES[step_type]

        # Check required fields
        for required_field in step_info['required']:
            if required_field not in step:
                errors.append(
                    f"Step ({step_name}): Type '{step_type}' requires field '{required_field}'. "
                    f"Expected YAML like:\n  - name: {step_name}\n    type: {step_type}\n    {required_field}: <value>"
                )

        # Validate specific field types
        if step_type == 'prompt' and 'prompt' in step:
            if not isinstance(step['prompt'], str):
                errors.append(f"Step ({step_name}): Field 'prompt' must be a string")

        elif step_type == 'template' and 'template_id' in step:
            if not isinstance(step['template_id'], str):
                errors.append(f"Step ({step_name}): Field 'template_id' must be a string")

        elif step_type == 'conditional':
            if 'condition' in step and not isinstance(step['condition'], str):
                errors.append(f"Step ({step_name}): Field 'condition' must be a string")

            if 'then' in step and not isinstance(step['then'], dict):
                errors.append(f"Step ({step_name}): Field 'then' must be a dictionary with 'type' field")

        elif step_type == 'loop':
            if 'items_var' in step and not isinstance(step['items_var'], str):
                errors.append(f"Step ({step_name}): Field 'items_var' must be a variable name (string)")

            if 'body' in step and not isinstance(step['body'], dict):
                errors.append(f"Step ({step_name}): Field 'body' must be a dictionary with 'type' field")

        elif step_type == 'sleep' and 'duration' in step:
            try:
                duration = float(step['duration'])
                if duration < 0:
                    errors.append(f"Step ({step_name}): Field 'duration' must be non-negative")
            except (ValueError, TypeError):
                errors.append(f"Step ({step_name}): Field 'duration' must be a number (seconds)")

        return errors

    @staticmethod
    def _validate_timeout(timeout: Any, step_name: str) -> List[str]:
        """Validate timeout field"""
        errors = []

        try:
            timeout_val = int(timeout)
        except (ValueError, TypeError):
            errors.append(
                f"Step ({step_name}): Field 'timeout' must be an integer (seconds), "
                f"got '{timeout}'"
            )
            return errors

        if timeout_val < WorkflowValidator.TIMEOUT_MIN or timeout_val > WorkflowValidator.TIMEOUT_MAX:
            errors.append(
                f"Step ({step_name}): Field 'timeout' must be between "
                f"{WorkflowValidator.TIMEOUT_MIN}-{WorkflowValidator.TIMEOUT_MAX} seconds, "
                f"got {timeout_val}"
            )

        return errors

    @staticmethod
    def _validate_retry(retry: Any, step_name: str) -> List[str]:
        """Validate retry configuration"""
        errors = []

        if not isinstance(retry, dict):
            errors.append(f"Step ({step_name}): Field 'retry' must be a dictionary")
            return errors

        # Validate max_attempts
        if 'max_attempts' in retry:
            try:
                max_attempts = int(retry['max_attempts'])
            except (ValueError, TypeError):
                errors.append(
                    f"Step ({step_name}): Retry field 'max_attempts' must be an integer, "
                    f"got '{retry['max_attempts']}'"
                )
                return errors

            if max_attempts < WorkflowValidator.RETRY_MIN_ATTEMPTS or \
               max_attempts > WorkflowValidator.RETRY_MAX_ATTEMPTS:
                errors.append(
                    f"Step ({step_name}): Retry field 'max_attempts' must be between "
                    f"{WorkflowValidator.RETRY_MIN_ATTEMPTS}-{WorkflowValidator.RETRY_MAX_ATTEMPTS}, "
                    f"got {max_attempts}"
                )

        # Validate backoff type
        if 'backoff' in retry:
            backoff = retry['backoff']
            if backoff not in WorkflowValidator.RETRY_BACKOFF_TYPES:
                errors.append(
                    f"Step ({step_name}): Retry field 'backoff' must be one of "
                    f"{WorkflowValidator.RETRY_BACKOFF_TYPES}, got '{backoff}'"
                )

        return errors

    @staticmethod
    def _validate_condition(condition: str, step_name: str) -> List[str]:
        """Validate condition syntax"""
        errors = []

        if not isinstance(condition, str):
            errors.append(f"Step ({step_name}): Field 'condition' must be a string")
            return errors

        # Check for common issues
        if '{{' not in condition and '}}' not in condition:
            # Might be using new condition syntax, which is fine
            pass

        # Warn about deprecated simple syntax if using it
        if ' == ' in condition or ' != ' in condition:
            # Old-style condition, which still works
            pass

        return errors

    @staticmethod
    def get_validation_summary(errors: List[str]) -> str:
        """
        Format validation errors for display

        Args:
            errors: List of error messages

        Returns:
            Formatted error summary
        """
        if not errors:
            return "Validation passed!"

        summary = f"Validation failed with {len(errors)} error(s):\n\n"
        for i, error in enumerate(errors, 1):
            summary += f"{i}. {error}\n"

        return summary
