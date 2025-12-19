#!/usr/bin/env python3
"""
Quick Validation Script - AI Router Enhanced Installation
Checks: files exist, modules import, databases initialize
Fast validation without running actual AI models
"""

import sys
from pathlib import Path
from typing import Tuple, List, Dict

# Colors for terminal output (works on Windows 10+ and Unix)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class InstallationValidator:
    """Validates all AI Router Enhanced components"""

    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0

    def validate_all_components(self) -> bool:
        """Run all validation checks"""
        print("=" * 70)
        print(f"{BLUE}AI ROUTER ENHANCED - INSTALLATION VALIDATOR{RESET}")
        print("=" * 70)
        print(f"Directory: {self.models_dir}")
        print()

        # Core files check
        self.section("CORE FILES")
        self.check_file_exists("ai-router.py", "Main AI Router script")
        self.check_file_exists("ai-router-enhanced.py", "Enhanced AI Router")
        self.check_file_exists("schema.sql", "Database schema")

        # Feature modules check
        self.section("FEATURE MODULES")
        self.check_module_import("session_manager", "Session Manager")
        self.check_module_import("template_manager", "Template Manager")
        self.check_module_import("context_manager", "Context Manager")
        self.check_module_import("response_processor", "Response Processor")
        self.check_module_import("model_selector", "Model Selector")
        self.check_module_import("model_comparison", "Model Comparison")
        self.check_module_import("batch_processor", "Batch Processor")
        self.check_module_import("analytics_dashboard", "Analytics Dashboard")
        self.check_module_import("workflow_engine", "Workflow Engine")

        # Directory structure
        self.section("DIRECTORY STRUCTURE")
        self.check_directory_exists("providers", "Provider modules")
        self.check_directory_optional("prompt_templates", "Prompt templates")
        self.check_directory_optional("workflows", "Workflow definitions")
        self.check_directory_optional("sessions", "Session storage")

        # Database initialization
        self.section("DATABASE INITIALIZATION")
        self.check_database_init()

        # Dependencies check
        self.section("PYTHON DEPENDENCIES")
        self.check_dependency("yaml", "PyYAML", required=True)
        self.check_dependency("jinja2", "Jinja2", required=True)
        self.check_dependency("requests", "Requests", required=True)
        self.check_dependency("sqlite3", "SQLite3", required=True)
        self.check_dependency("tiktoken", "TikTok", required=False)

        # Provider checks
        self.section("PROVIDERS")
        self.check_provider("ollama_provider", "Ollama Provider")
        self.check_provider("llama_cpp_provider", "Llama.cpp Provider")
        self.check_provider("openai_provider", "OpenAI Provider")
        self.check_provider("claude_provider", "Claude Provider")
        self.check_provider("openrouter_provider", "OpenRouter Provider")

        # Configuration checks
        self.section("CONFIGURATION")
        self.check_configuration()

        # Print summary
        self.print_summary()

        return self.checks_failed == 0

    def section(self, title: str):
        """Print section header"""
        print()
        print(f"{YELLOW}[{title}]{RESET}")

    def check_file_exists(self, filename: str, description: str) -> bool:
        """Check if a file exists"""
        file_path = self.models_dir / filename
        if file_path.exists():
            self.pass_check(f"{description}: {filename}")
            return True
        else:
            self.fail_check(f"{description}: {filename} NOT FOUND")
            return False

    def check_directory_exists(self, dirname: str, description: str) -> bool:
        """Check if a directory exists (required)"""
        dir_path = self.models_dir / dirname
        if dir_path.exists() and dir_path.is_dir():
            self.pass_check(f"{description}: {dirname}/")
            return True
        else:
            self.fail_check(f"{description}: {dirname}/ NOT FOUND")
            return False

    def check_directory_optional(self, dirname: str, description: str) -> bool:
        """Check if a directory exists (optional)"""
        dir_path = self.models_dir / dirname
        if dir_path.exists() and dir_path.is_dir():
            self.pass_check(f"{description}: {dirname}/")
            return True
        else:
            self.warn_check(f"{description}: {dirname}/ not found (will be created on first use)")
            return False

    def check_module_import(self, module_name: str, description: str) -> bool:
        """Check if a Python module can be imported"""
        sys.path.insert(0, str(self.models_dir))

        try:
            __import__(module_name)
            self.pass_check(f"{description}: import {module_name}")
            return True
        except ImportError as e:
            self.fail_check(f"{description}: import {module_name} FAILED - {e}")
            return False
        except Exception as e:
            self.fail_check(f"{description}: import {module_name} ERROR - {e}")
            return False

    def check_dependency(self, module_name: str, package_name: str, required: bool = True) -> bool:
        """Check if a Python dependency is installed"""
        try:
            __import__(module_name)
            self.pass_check(f"{package_name}: installed")
            return True
        except ImportError:
            if required:
                self.fail_check(f"{package_name}: NOT INSTALLED (required)")
                return False
            else:
                self.warn_check(f"{package_name}: not installed (optional)")
                return False

    def check_provider(self, module_name: str, description: str) -> bool:
        """Check if a provider module exists"""
        provider_path = self.models_dir / "providers" / f"{module_name}.py"
        if provider_path.exists():
            self.pass_check(f"{description}: providers/{module_name}.py")
            return True
        else:
            self.warn_check(f"{description}: providers/{module_name}.py not found")
            return False

    def check_database_init(self) -> bool:
        """Check database initialization"""
        try:
            from session_manager import SessionManager

            # Create test database
            test_db = self.models_dir / "test_validation.db"
            if test_db.exists():
                test_db.unlink()

            sm = SessionManager(test_db)

            # Try creating a session
            session_id = sm.create_session("test_model")

            if session_id:
                self.pass_check("Database initialization and session creation")
                # Cleanup
                test_db.unlink()
                return True
            else:
                self.fail_check("Database session creation failed")
                return False

        except Exception as e:
            self.fail_check(f"Database initialization failed: {e}")
            return False

    def check_configuration(self):
        """Check configuration files and environment"""
        # Check for model configuration
        models_exist = False

        # Check if any models are configured
        try:
            from ai_router import AIRouter
            # This would need the actual router implementation
            self.warn_check("Model configuration check skipped (requires manual verification)")
        except:
            self.warn_check("Configuration check skipped (manual verification recommended)")

    def pass_check(self, message: str):
        """Record passed check"""
        self.checks_passed += 1
        print(f"  {GREEN}[OK]{RESET} {message}")

    def fail_check(self, message: str):
        """Record failed check"""
        self.checks_failed += 1
        print(f"  {RED}[FAIL]{RESET} {message}")

    def warn_check(self, message: str):
        """Record warning"""
        self.warnings += 1
        print(f"  {YELLOW}[WARN]{RESET} {message}")

    def print_summary(self):
        """Print validation summary"""
        total = self.checks_passed + self.checks_failed

        print()
        print("=" * 70)
        print(f"{BLUE}VALIDATION SUMMARY{RESET}")
        print("=" * 70)
        print(f"Checks Passed: {GREEN}{self.checks_passed}{RESET}")
        print(f"Checks Failed: {RED}{self.checks_failed}{RESET}")
        print(f"Warnings: {YELLOW}{self.warnings}{RESET}")
        print(f"Total Checks: {total}")
        print()

        if self.checks_failed == 0:
            print(f"{GREEN}All critical checks passed!{RESET}")
            print("Your AI Router Enhanced installation appears to be correct.")
            if self.warnings > 0:
                print(f"\n{YELLOW}Note: {self.warnings} warnings detected.{RESET}")
                print("Optional features may not be fully configured.")
        else:
            print(f"{RED}Installation has issues!{RESET}")
            print(f"{self.checks_failed} critical check(s) failed.")
            print("Please review the errors above and fix missing components.")

        print()
        print("=" * 70)


def main():
    """Main entry point"""
    models_dir = Path(__file__).parent

    validator = InstallationValidator(models_dir)
    success = validator.validate_all_components()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
