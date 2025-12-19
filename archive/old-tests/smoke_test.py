#!/usr/bin/env python3
"""
Smoke Test - Quick 2-minute validation of AI Router Enhanced
Tests basic functionality without executing models
Just imports and initialization
"""

import sys
from pathlib import Path
import time


class SmokeTest:
    """Quick smoke test for basic functionality"""

    def __init__(self):
        self.models_dir = Path(__file__).parent
        sys.path.insert(0, str(self.models_dir))
        self.tests_run = 0
        self.tests_passed = 0
        self.start_time = time.time()

    def run(self):
        """Run all smoke tests"""
        print("=" * 60)
        print("AI ROUTER ENHANCED - SMOKE TEST")
        print("Quick validation (no model execution)")
        print("=" * 60)
        print()

        # Test 1: Import all modules
        self.test("Import all feature modules", self.test_imports)

        # Test 2: Database creation
        self.test("Create session database", self.test_database)

        # Test 3: Template loading
        self.test("Load prompt templates", self.test_templates)

        # Test 4: Context manager
        self.test("Initialize context manager", self.test_context)

        # Test 5: Batch processor
        self.test("Initialize batch processor", self.test_batch)

        # Test 6: Workflow engine
        self.test("Initialize workflow engine", self.test_workflows)

        # Test 7: Analytics
        self.test("Initialize analytics", self.test_analytics)

        # Test 8: Model comparison
        self.test("Initialize model comparison", self.test_comparison)

        # Test 9: Response processor
        self.test("Initialize response processor", self.test_response_processor)

        # Summary
        self.print_summary()

    def test(self, name: str, test_func):
        """Run a single test"""
        self.tests_run += 1
        print(f"[{self.tests_run}] {name}...", end=" ")

        try:
            test_func()
            self.tests_passed += 1
            print("[OK]")
            return True
        except Exception as e:
            print(f"[FAIL] {e}")
            return False

    def test_imports(self):
        """Test importing all modules"""
        from session_manager import SessionManager
        from template_manager import TemplateManager, PromptTemplate
        from context_manager import ContextManager
        from response_processor import ResponseProcessor
        from model_selector import ModelSelector
        from model_comparison import ModelComparison
        from batch_processor import BatchProcessor
        from analytics_dashboard import AnalyticsDashboard
        from workflow_engine import WorkflowEngine

    def test_database(self):
        """Test database creation"""
        from session_manager import SessionManager

        test_db = self.models_dir / "smoke_test.db"
        if test_db.exists():
            test_db.unlink()

        sm = SessionManager(test_db)
        assert test_db.exists()

        # Cleanup
        test_db.unlink()

    def test_templates(self):
        """Test template system"""
        from template_manager import TemplateManager

        templates_dir = self.models_dir / "prompt_templates"
        if not templates_dir.exists():
            templates_dir.mkdir()

        # Create test template
        test_template = templates_dir / "smoke_test.yaml"
        test_template.write_text("""
metadata:
  name: Smoke Test
  description: Test template

user_prompt: |
  Test prompt
""")

        tm = TemplateManager(templates_dir)
        templates = tm.list_templates()

        # Cleanup
        test_template.unlink()

    def test_context(self):
        """Test context manager"""
        from context_manager import ContextManager

        cm = ContextManager()

        # Test file
        test_file = self.models_dir / "smoke_context.txt"
        test_file.write_text("Test content")

        content = cm.load_file(test_file)
        assert "Test content" in content

        # Cleanup
        test_file.unlink()

    def test_batch(self):
        """Test batch processor"""
        from batch_processor import BatchProcessor

        checkpoint_dir = self.models_dir / "smoke_checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)

        bp = BatchProcessor(checkpoint_dir)
        job = bp.create_job("test_model", ["p1", "p2"])
        assert job.total_prompts == 2

        # Cleanup
        import shutil
        shutil.rmtree(checkpoint_dir)

    def test_workflows(self):
        """Test workflow engine"""
        from workflow_engine import WorkflowEngine

        workflows_dir = self.models_dir / "smoke_workflows"
        workflows_dir.mkdir(exist_ok=True)

        # Create test workflow
        test_workflow = workflows_dir / "smoke.yaml"
        test_workflow.write_text("""
name: Smoke Test Workflow
description: Test

steps:
  - name: step1
    type: prompt
    config:
      prompt: test
""")

        class MockRouter:
            pass

        we = WorkflowEngine(workflows_dir, MockRouter())

        # Cleanup
        import shutil
        shutil.rmtree(workflows_dir)

    def test_analytics(self):
        """Test analytics dashboard"""
        from session_manager import SessionManager
        from analytics_dashboard import AnalyticsDashboard

        test_db = self.models_dir / "smoke_analytics.db"
        if test_db.exists():
            test_db.unlink()

        sm = SessionManager(test_db)
        dashboard = AnalyticsDashboard(sm)

        # Cleanup
        test_db.unlink()

    def test_comparison(self):
        """Test model comparison"""
        from model_comparison import ModelComparison

        results_dir = self.models_dir / "smoke_comparisons"
        results_dir.mkdir(exist_ok=True)

        mc = ModelComparison(results_dir)
        comparison = mc.create_comparison("Test")

        # Cleanup
        import shutil
        shutil.rmtree(results_dir)

    def test_response_processor(self):
        """Test response processor"""
        from response_processor import ResponseProcessor

        processor = ResponseProcessor()
        result = processor.format_markdown("Test", "model1", 10, 5, 1.0)
        assert "Test" in result

    def print_summary(self):
        """Print test summary"""
        elapsed = time.time() - self.start_time

        print()
        print("=" * 60)
        print("SMOKE TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Time: {elapsed:.2f}s")
        print()

        if self.tests_passed == self.tests_run:
            print("[SUCCESS] All smoke tests passed!")
            print("Basic functionality is working correctly.")
        else:
            print("[FAILURE] Some tests failed!")
            print("Please review errors above.")

        print("=" * 60)


def main():
    """Main entry point"""
    test = SmokeTest()
    test.run()

    # Exit with error code if any test failed
    sys.exit(0 if test.tests_passed == test.tests_run else 1)


if __name__ == "__main__":
    main()
