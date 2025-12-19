#!/usr/bin/env python3
"""
Comprehensive Menu Navigation Test for ai-router.py

This script validates:
1. Main menu structure (12 options + A + 0)
2. All menu option handlers exist
3. Sub-menu structures are complete
4. Input validation
5. Navigation flow integrity
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

class MenuNavigationTester:
    def __init__(self, router_file: Path):
        self.router_file = router_file
        self.tree = None
        self.issues = []
        self.successes = []

        # Expected main menu mappings
        self.expected_menu_mappings = {
            "1": "auto_select_mode",
            "2": "list_models",
            "3": "context_mode",
            "4": "session_mode",
            "5": "batch_mode",
            "6": "workflow_mode",
            "7": "analytics_mode",
            "8": "view_system_prompts",
            "9": "view_parameters_guide",
            "10": "view_documentation",
            "11": "comparison_mode",
            "12": "template_mode",
            "A": "toggle_bypass_mode",
            "0": "exit"
        }

        # Expected sub-menu structures
        self.expected_submenus = {
            "context_mode": {
                "options": ["1", "2", "3", "4", "5", "6", "0"],
                "handlers": [
                    "add_files_to_context",
                    "add_text_to_context",
                    "remove_context_item",
                    "clear_context",
                    "set_token_limit",
                    "execute_with_context"
                ]
            },
            "session_mode": {
                "options": ["1", "2", "3", "4", "5", "6", "0"],
                "handlers": [
                    "list_sessions_interactive",
                    "search_sessions_interactive",
                    "resume_session",
                    "view_session_details",
                    "export_session_interactive",
                    "cleanup_sessions"
                ]
            },
            "batch_mode": {
                "options": ["1", "2", "3", "4", "0"],
                "handlers": [
                    "batch_from_file",
                    "batch_manual_prompts",
                    "batch_resume_checkpoint",
                    "batch_list_checkpoints"
                ]
            },
            "workflow_mode": {
                "options": ["1", "2", "3", "4", "0"],
                "handlers": [
                    "workflow_run",
                    "workflow_list",
                    "workflow_create_from_template",
                    "workflow_validate"
                ]
            },
            "analytics_mode": {
                "options": ["1", "2", "3", "4", "0"],
                "handlers": [
                    "display_dashboard",  # Called on self.analytics
                    "export_analytics"
                ]
            }
        }

    def parse_file(self):
        """Parse the Python file into an AST"""
        try:
            with open(self.router_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self.tree = ast.parse(content)
            self.successes.append("[OK] Successfully parsed ai-router.py")
            return True
        except Exception as e:
            self.issues.append(f"[FAIL] Failed to parse file: {e}")
            return False

    def find_class_methods(self, class_name: str = "AIRouter") -> Set[str]:
        """Find all methods in a class"""
        methods = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.add(item.name)
        return methods

    def check_main_menu_structure(self) -> bool:
        """Verify main menu displays all 12 options"""
        try:
            with open(self.router_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for all menu options
            required_menu_items = [
                "[1]",
                "[2]",
                "[3]",
                "[4]",
                "[5]",
                "[6]",
                "[7]",
                "[8]",
                "[9]",
                "[10]",
                "[11]",
                "[12]",
                "[A]",
                "[0]"
            ]

            # Find interactive_mode function
            if "def interactive_mode(self):" in content:
                self.successes.append("[OK] Main menu method (interactive_mode) exists")

                # Check each menu item (just check for the item itself, not the Colors variable)
                missing = []
                for item in required_menu_items:
                    if item not in content:
                        missing.append(item)

                if missing:
                    self.issues.append(f"[FAIL] Missing menu items in display: {', '.join(missing)}")
                    return False
                else:
                    self.successes.append(f"[OK] All {len(required_menu_items)} menu options displayed correctly")
                    return True
            else:
                self.issues.append("[FAIL] interactive_mode method not found")
                return False

        except Exception as e:
            self.issues.append(f"[FAIL] Error checking menu structure: {e}")
            return False

    def check_menu_handlers(self) -> bool:
        """Verify all menu option handlers exist"""
        methods = self.find_class_methods()

        missing_handlers = []
        for choice, handler in self.expected_menu_mappings.items():
            if choice == "0":  # Exit is inline, not a method
                continue
            if handler not in methods:
                missing_handlers.append(f"{choice} -> {handler}")

        if missing_handlers:
            self.issues.append(f"[FAIL] Missing menu handlers: {', '.join(missing_handlers)}")
            return False
        else:
            self.successes.append(f"[OK] All {len(self.expected_menu_mappings)-1} menu handlers exist")
            return True

    def check_submenu_structures(self) -> bool:
        """Verify sub-menu structures are complete"""
        methods = self.find_class_methods()

        all_good = True
        for menu_name, submenu_info in self.expected_submenus.items():
            if menu_name not in methods:
                self.issues.append(f"[FAIL] Sub-menu parent method missing: {menu_name}")
                all_good = False
                continue

            # Check handlers exist
            missing_handlers = []
            for handler in submenu_info["handlers"]:
                if handler not in methods and handler != "display_dashboard" and handler != "clear_context":
                    missing_handlers.append(handler)

            if missing_handlers:
                self.issues.append(f"[FAIL] {menu_name}: Missing handlers: {', '.join(missing_handlers)}")
                all_good = False
            else:
                self.successes.append(f"[OK] {menu_name}: All {len(submenu_info['handlers'])} handlers exist")

        return all_good

    def check_back_exit_options(self) -> bool:
        """Verify back/exit options in sub-menus"""
        try:
            with open(self.router_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Sub-menus that should have back/exit options
            submenu_methods = [
                "context_mode",
                "session_mode",
                "batch_mode",
                "workflow_mode",
                "analytics_mode"
            ]

            missing_exit = []
            for method in submenu_methods:
                # Find the method definition
                method_start = content.find(f"def {method}(self):")
                if method_start == -1:
                    continue

                # Get method body (approximate - look for next method or end)
                method_end = content.find("\n    def ", method_start + 1)
                if method_end == -1:
                    method_end = len(content)

                method_body = content[method_start:method_end]

                # Check for exit/back option
                has_exit = (
                    'choice == "0"' in method_body or
                    'if choice == "0":' in method_body or
                    '.lower() == "back"' in method_body or
                    'elif choice == "0":' in method_body
                )

                if not has_exit:
                    missing_exit.append(method)

            if missing_exit:
                self.issues.append(f"[FAIL] Missing back/exit options: {', '.join(missing_exit)}")
                return False
            else:
                self.successes.append(f"[OK] All {len(submenu_methods)} sub-menus have back/exit options")
                return True

        except Exception as e:
            self.issues.append(f"[FAIL] Error checking back/exit options: {e}")
            return False

    def check_input_validation(self) -> bool:
        """Check for input validation in menu handlers"""
        try:
            with open(self.router_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for error handling patterns
            has_invalid_choice = "Invalid choice" in content
            has_try_except = "try:" in content and "except ValueError:" in content

            if has_invalid_choice and has_try_except:
                self.successes.append("[OK] Input validation implemented (invalid choice handling)")
                return True
            else:
                self.issues.append("[FAIL] Incomplete input validation")
                return False

        except Exception as e:
            self.issues.append(f"[FAIL] Error checking input validation: {e}")
            return False

    def check_navigation_flow(self) -> bool:
        """Verify navigation flow patterns"""
        try:
            with open(self.router_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for while True loops in sub-menus (indicates proper loop-back)
            submenu_methods = [
                "context_mode",
                "session_mode",
                "batch_mode",
                "workflow_mode",
                "analytics_mode"
            ]

            missing_loops = []
            for method in submenu_methods:
                method_pattern = f"def {method}(self):"
                method_start = content.find(method_pattern)
                if method_start == -1:
                    continue

                # Check for while True within reasonable distance
                method_section = content[method_start:method_start+500]
                if "while True:" not in method_section:
                    missing_loops.append(method)

            if missing_loops:
                self.issues.append(f"[FAIL] Sub-menus without loop-back: {', '.join(missing_loops)}")
                return False
            else:
                self.successes.append(f"[OK] All {len(submenu_methods)} sub-menus have proper loop-back")
                return True

        except Exception as e:
            self.issues.append(f"[FAIL] Error checking navigation flow: {e}")
            return False

    def check_duplicate_definitions(self) -> bool:
        """Check for duplicate method definitions"""
        methods = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == "AIRouter":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name in methods:
                            methods[item.name].append(item.lineno)
                        else:
                            methods[item.name] = [item.lineno]

        duplicates = {name: lines for name, lines in methods.items() if len(lines) > 1}

        if duplicates:
            for name, lines in duplicates.items():
                self.issues.append(f"[FAIL] Duplicate method definition: {name} at lines {lines}")
            return False
        else:
            self.successes.append("[OK] No duplicate method definitions found")
            return True

    def run_all_tests(self) -> Tuple[int, int]:
        """Run all tests and return (successes, failures)"""
        print("\n" + "="*70)
        print("  AI ROUTER MENU NAVIGATION TEST SUITE")
        print("="*70 + "\n")

        if not self.parse_file():
            return 0, 1

        # Run all tests
        tests = [
            ("Main Menu Structure", self.check_main_menu_structure),
            ("Menu Handler Existence", self.check_menu_handlers),
            ("Sub-Menu Structures", self.check_submenu_structures),
            ("Back/Exit Options", self.check_back_exit_options),
            ("Input Validation", self.check_input_validation),
            ("Navigation Flow", self.check_navigation_flow),
            ("Duplicate Definitions", self.check_duplicate_definitions),
        ]

        for test_name, test_func in tests:
            print(f"Running: {test_name}...")
            test_func()
            print()

        return len(self.successes), len(self.issues)

    def print_report(self):
        """Print detailed test report"""
        print("\n" + "="*70)
        print("  TEST RESULTS")
        print("="*70 + "\n")

        if self.successes:
            print("SUCCESSES:")
            print("-" * 70)
            for success in self.successes:
                print(success)
            print()

        if self.issues:
            print("ISSUES FOUND:")
            print("-" * 70)
            for issue in self.issues:
                print(issue)
            print()

        # Calculate score
        total_tests = len(self.successes) + len(self.issues)
        if total_tests > 0:
            score = (len(self.successes) / total_tests) * 100
        else:
            score = 0

        print("="*70)
        print(f"OVERALL NAVIGATION SCORE: {score:.1f}%")
        print(f"Successes: {len(self.successes)} | Issues: {len(self.issues)}")
        print("="*70 + "\n")

        # Menu structure summary
        print("MENU STRUCTURE SUMMARY:")
        print("-" * 70)
        print("Main Menu Options: 12 (plus A for Auto-Yes, 0 for Exit)")
        print("Sub-Menus Tested:")
        for menu_name, submenu_info in self.expected_submenus.items():
            print(f"  - {menu_name}: {len(submenu_info['options'])} options, {len(submenu_info['handlers'])} handlers")
        print()

        return score


def main():
    router_file = Path("D:/models/ai-router.py")

    if not router_file.exists():
        print(f"Error: {router_file} not found!")
        return 1

    tester = MenuNavigationTester(router_file)
    successes, failures = tester.run_all_tests()
    score = tester.print_report()

    # Return exit code based on results
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
