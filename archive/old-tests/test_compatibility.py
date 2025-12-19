#!/usr/bin/env python3
"""
Compatibility Test - Test AI Router Enhanced across different environments
Tests: Windows, optional dependencies, Python versions
"""

import sys
import platform
from pathlib import Path
import subprocess


class CompatibilityTest:
    """Test compatibility across environments"""

    def __init__(self):
        self.models_dir = Path(__file__).parent
        sys.path.insert(0, str(self.models_dir))
        self.checks_passed = 0
        self.checks_failed = 0

    def run_all_tests(self):
        """Run all compatibility tests"""
        print("=" * 70)
        print("AI ROUTER ENHANCED - COMPATIBILITY TEST")
        print("=" * 70)
        print()

        # Platform information
        self.print_platform_info()

        # Python version check
        self.section("PYTHON VERSION")
        self.check_python_version()

        # Core dependencies
        self.section("CORE DEPENDENCIES")
        self.check_core_dependencies()

        # Optional dependencies
        self.section("OPTIONAL DEPENDENCIES")
        self.check_optional_dependencies()

        # Windows-specific checks
        if platform.system() == "Windows":
            self.section("WINDOWS COMPATIBILITY")
            self.check_windows_compatibility()

        # Linux/WSL checks
        if platform.system() == "Linux":
            self.section("LINUX/WSL COMPATIBILITY")
            self.check_linux_compatibility()

        # File system compatibility
        self.section("FILE SYSTEM")
        self.check_filesystem_compatibility()

        # Import compatibility
        self.section("MODULE IMPORTS")
        self.check_module_imports()

        # Summary
        self.print_summary()

    def section(self, title: str):
        """Print section header"""
        print()
        print(f"[{title}]")
        print("-" * 70)

    def print_platform_info(self):
        """Print platform information"""
        print("Platform Information:")
        print(f"  OS: {platform.system()} {platform.release()}")
        print(f"  Python Version: {sys.version}")
        print(f"  Architecture: {platform.machine()}")
        print(f"  Python Implementation: {platform.python_implementation()}")

    def check_python_version(self):
        """Check Python version compatibility"""
        version = sys.version_info

        if version >= (3, 8):
            self.pass_check(f"Python {version.major}.{version.minor}.{version.micro} (>= 3.8)")
        else:
            self.fail_check(f"Python {version.major}.{version.minor}.{version.micro} (requires >= 3.8)")

        # Check for specific version features
        if version >= (3, 9):
            self.pass_check("Python 3.9+ features available (dict union operators)")

        if version >= (3, 10):
            self.pass_check("Python 3.10+ features available (match statements)")

    def check_core_dependencies(self):
        """Check core required dependencies"""
        dependencies = [
            ("yaml", "PyYAML"),
            ("jinja2", "Jinja2"),
            ("sqlite3", "SQLite3"),
            ("json", "JSON"),
            ("pathlib", "pathlib"),
        ]

        for module, name in dependencies:
            try:
                __import__(module)
                self.pass_check(f"{name}: installed")
            except ImportError:
                self.fail_check(f"{name}: NOT INSTALLED (required)")

    def check_optional_dependencies(self):
        """Check optional dependencies"""
        optional_deps = [
            ("tiktoken", "TikTok (for token counting)", "OpenAI token estimation"),
            ("requests", "Requests (for HTTP)", "API calls"),
            ("pandas", "Pandas (for analytics)", "Enhanced analytics"),
            ("matplotlib", "Matplotlib (for charts)", "Visualization"),
        ]

        for module, name, feature in optional_deps:
            try:
                __import__(module)
                self.pass_check(f"{name}: installed - {feature} available")
            except ImportError:
                print(f"  [INFO] {name}: not installed - {feature} unavailable")

    def check_windows_compatibility(self):
        """Check Windows-specific compatibility"""
        # Check for ANSI color support
        try:
            import colorama
            colorama.init()
            self.pass_check("Colorama available (terminal colors)")
        except ImportError:
            print("  [INFO] Colorama not available (colors may not work)")

        # Check path handling
        test_path = Path("D:\\test\\path")
        if test_path.drive == "D:":
            self.pass_check("Windows path handling works correctly")

        # Check for WSL detection
        try:
            with open("/proc/version", "r") as f:
                content = f.read().lower()
                if "microsoft" in content or "wsl" in content:
                    print("  [INFO] Running in WSL environment")
        except:
            pass

    def check_linux_compatibility(self):
        """Check Linux/WSL compatibility"""
        # Check terminal capabilities
        try:
            import termios
            self.pass_check("Terminal control available (termios)")
        except ImportError:
            print("  [INFO] termios not available")

        # Check for WSL
        try:
            with open("/proc/version", "r") as f:
                content = f.read().lower()
                if "microsoft" in content or "wsl" in content:
                    self.pass_check("WSL environment detected")
                    # Check for Windows path access
                    windows_path = Path("/mnt/c")
                    if windows_path.exists():
                        self.pass_check("Windows filesystem accessible via /mnt/c")
        except Exception:
            pass

    def check_filesystem_compatibility(self):
        """Check filesystem operations"""
        # Test directory creation
        test_dir = self.models_dir / "test_compat_dir"
        try:
            test_dir.mkdir(exist_ok=True)
            self.pass_check("Directory creation works")
            test_dir.rmdir()
        except Exception as e:
            self.fail_check(f"Directory creation failed: {e}")

        # Test file creation
        test_file = self.models_dir / "test_compat_file.txt"
        try:
            test_file.write_text("Test content")
            content = test_file.read_text()
            if content == "Test content":
                self.pass_check("File read/write works")
            test_file.unlink()
        except Exception as e:
            self.fail_check(f"File operations failed: {e}")

        # Test path operations
        try:
            absolute_path = test_file.resolve()
            self.pass_check("Path resolution works")
        except Exception as e:
            self.fail_check(f"Path resolution failed: {e}")

    def check_module_imports(self):
        """Check if all modules can be imported"""
        modules = [
            "session_manager",
            "template_manager",
            "context_manager",
            "response_processor",
            "model_selector",
            "model_comparison",
            "batch_processor",
            "analytics_dashboard",
            "workflow_engine",
        ]

        for module in modules:
            try:
                __import__(module)
                self.pass_check(f"Import {module}")
            except ImportError as e:
                self.fail_check(f"Import {module} failed: {e}")
            except Exception as e:
                self.fail_check(f"Import {module} error: {e}")

    def pass_check(self, message: str):
        """Record passed check"""
        self.checks_passed += 1
        print(f"  [OK] {message}")

    def fail_check(self, message: str):
        """Record failed check"""
        self.checks_failed += 1
        print(f"  [FAIL] {message}")

    def print_summary(self):
        """Print compatibility summary"""
        total = self.checks_passed + self.checks_failed

        print()
        print("=" * 70)
        print("COMPATIBILITY SUMMARY")
        print("=" * 70)
        print(f"Checks Passed: {self.checks_passed}/{total}")
        print(f"Checks Failed: {self.checks_failed}/{total}")
        print()

        if self.checks_failed == 0:
            print("[SUCCESS] All compatibility checks passed!")
            print("AI Router Enhanced is compatible with this environment.")
        else:
            print(f"[WARNING] {self.checks_failed} compatibility issue(s) found.")
            print("Some features may not work correctly.")

        print("=" * 70)


def main():
    """Main entry point"""
    test = CompatibilityTest()
    test.run_all_tests()

    sys.exit(0 if test.checks_failed == 0 else 1)


if __name__ == "__main__":
    main()
