#!/usr/bin/env python3
"""
Configuration Validator for AI Router
Validates machine-specific configuration files and provides helpful error messages
"""

import json
import sys
from pathlib import Path
from typing import Dict, Tuple, List


class ConfigValidator:
    """Validates AI Router configuration files"""

    # Required top-level fields
    REQUIRED_FIELDS = ['machine', 'models', 'performance', 'inference']

    # Required fields in each section
    REQUIRED_SUBFIELDS = {
        'machine': ['id', 'name', 'specs', 'platform'],
        'models': ['primary', 'enabled'],
        'performance': ['max_tokens', 'batch_size', 'temperature', 'top_p'],
        'inference': ['backend', 'device', 'dtype']
    }

    # Valid values for certain fields
    VALID_VALUES = {
        'inference.backend': ['vllm', 'llama.cpp', 'ollama', 'mlx', 'transformers'],
        'inference.device': ['cuda', 'cpu', 'mps', 'metal'],
        'inference.dtype': ['float32', 'float16', 'bfloat16', 'int8', 'int4'],
        'machine.platform': ['Linux', 'Windows', 'Darwin']
    }

    @classmethod
    def validate_config(cls, config_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a configuration file
        Returns: (is_valid, list_of_errors)
        """
        errors = []

        # Check file exists
        if not config_path.exists():
            errors.append(f"Configuration file not found: {config_path}")
            return False, errors

        # Try to load JSON
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in config file: {e}")
            return False, errors
        except Exception as e:
            errors.append(f"Error reading config file: {e}")
            return False, errors

        # Validate structure
        cls._validate_required_fields(config, errors)
        cls._validate_subfields(config, errors)
        cls._validate_values(config, errors)
        cls._validate_ranges(config, errors)

        return len(errors) == 0, errors

    @classmethod
    def _validate_required_fields(
        cls, config: Dict, errors: List[str]
    ) -> None:
        """Check that all required top-level fields exist"""
        for field in cls.REQUIRED_FIELDS:
            if field not in config:
                errors.append(
                    f"Missing required field: '{field}'"
                )
            elif not isinstance(config[field], dict):
                errors.append(
                    f"Field '{field}' must be a dictionary, "
                    f"got {type(config[field]).__name__}"
                )

    @classmethod
    def _validate_subfields(
        cls, config: Dict, errors: List[str]
    ) -> None:
        """Check that required subfields exist in each section"""
        for section, required_fields in cls.REQUIRED_SUBFIELDS.items():
            if section not in config:
                continue

            section_config = config[section]
            if not isinstance(section_config, dict):
                continue

            for field in required_fields:
                if field not in section_config:
                    errors.append(
                        f"Missing required field in '{section}': '{field}'"
                    )

    @classmethod
    def _validate_values(cls, config: Dict, errors: List[str]) -> None:
        """Check that certain fields have valid values"""
        for key_path, valid_values in cls.VALID_VALUES.items():
            section, field = key_path.split('.')
            if section in config and field in config[section]:
                value = config[section][field]
                if value not in valid_values:
                    errors.append(
                        f"Invalid value for '{key_path}': '{value}'. "
                        f"Must be one of: {', '.join(valid_values)}"
                    )

    @classmethod
    def _validate_ranges(cls, config: Dict, errors: List[str]) -> None:
        """Check that numeric fields are in valid ranges"""
        if 'performance' in config:
            perf = config['performance']

            # Validate temperature
            if 'temperature' in perf:
                temp = perf['temperature']
                if not isinstance(temp, (int, float)):
                    errors.append(
                        f"'performance.temperature' must be a number, "
                        f"got {type(temp).__name__}"
                    )
                elif not (0.0 <= temp <= 2.0):
                    errors.append(
                        f"'performance.temperature' must be between 0.0 and 2.0, "
                        f"got {temp}"
                    )

            # Validate top_p
            if 'top_p' in perf:
                top_p = perf['top_p']
                if not isinstance(top_p, (int, float)):
                    errors.append(
                        f"'performance.top_p' must be a number, "
                        f"got {type(top_p).__name__}"
                    )
                elif not (0.0 <= top_p <= 1.0):
                    errors.append(
                        f"'performance.top_p' must be between 0.0 and 1.0, "
                        f"got {top_p}"
                    )

            # Validate batch_size
            if 'batch_size' in perf:
                batch = perf['batch_size']
                if not isinstance(batch, int):
                    errors.append(
                        f"'performance.batch_size' must be an integer, "
                        f"got {type(batch).__name__}"
                    )
                elif batch < 1:
                    errors.append(
                        f"'performance.batch_size' must be at least 1, "
                        f"got {batch}"
                    )

    @staticmethod
    def print_validation_report(
        config_path: Path, is_valid: bool, errors: List[str]
    ) -> None:
        """Print human-readable validation report"""
        from pathlib import Path
        import os

        # Color codes
        class C:
            RESET = '\033[0m'
            BOLD = '\033[1m'
            GREEN = '\033[32m'
            RED = '\033[31m'
            YELLOW = '\033[33m'
            BLUE = '\033[34m'
            CYAN = '\033[36m'

        print(f"\n{C.BOLD}{C.CYAN}Configuration Validation Report{C.RESET}")
        print("=" * 60)
        print(f"\nConfig File: {C.BLUE}{config_path}{C.RESET}")

        if is_valid:
            print(f"{C.GREEN}[OK] Configuration is valid!{C.RESET}\n")
        else:
            print(f"{C.RED}[ERROR] Configuration has issues:{C.RESET}\n")
            for idx, error in enumerate(errors, 1):
                print(
                    f"{C.RED}  [{idx}] {error}{C.RESET}"
                )
            print()

        return is_valid


def validate_and_report(machine_id: str, models_dir: Path) -> bool:
    """
    Validate config for a machine and print report
    Returns True if valid, False otherwise
    """
    config_path = models_dir / f"configs/{machine_id}/ai-router-config.json"

    validator = ConfigValidator()
    is_valid, errors = validator.validate_config(config_path)

    validator.print_validation_report(config_path, is_valid, errors)

    return is_valid


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python config_validator.py <path_to_config.json>")
        sys.exit(1)

    config_file = Path(sys.argv[1])
    validator = ConfigValidator()
    is_valid, errors = validator.validate_config(config_file)

    validator.print_validation_report(config_file, is_valid, errors)

    sys.exit(0 if is_valid else 1)
