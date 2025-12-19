#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for AI Router Enhanced
Tests all 9 features individually and in combination
"""

import sys
from pathlib import Path
import traceback
import time
from datetime import datetime
import json

# Add models directory to path
MODELS_DIR = Path(__file__).parent
sys.path.insert(0, str(MODELS_DIR))


class IntegrationTestSuite:
    """Run all integration tests"""

    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.start_time = None
        self.current_category = None

    def run_all_tests(self):
        """Execute all test categories"""
        self.start_time = time.time()

        print("=" * 70)
        print("AI ROUTER ENHANCED - INTEGRATION TEST SUITE")
        print("=" * 70)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Test Directory: {self.models_dir}")
        print()

        # Category 1: Core Infrastructure
        self.test_category("CORE INFRASTRUCTURE")
        self.test_session_manager()
        self.test_response_capture()

        # Category 2: Independent Features
        self.test_category("INDEPENDENT FEATURES")
        self.test_prompt_templates()
        self.test_context_management()
        self.test_response_processing()
        self.test_model_selector()

        # Category 3: Dependent Features
        self.test_category("DEPENDENT FEATURES")
        self.test_model_comparison()
        self.test_batch_processing()
        self.test_analytics()

        # Category 4: Advanced Features
        self.test_category("ADVANCED FEATURES")
        self.test_workflows()

        # Category 5: Integration Tests
        self.test_category("INTEGRATION TESTS")
        self.test_feature_interactions()

        # Summary
        self.print_summary()

    def test_category(self, category_name: str):
        """Print category header"""
        self.current_category = category_name
        print()
        print("-" * 70)
        print(f"CATEGORY: {category_name}")
        print("-" * 70)

    def run_test(self, test_name: str, test_func):
        """Run a single test with error handling"""
        test_id = f"{self.current_category}::{test_name}"
        print(f"\n[TEST] {test_name}...")

        try:
            start = time.time()
            test_func()
            duration = time.time() - start

            self.passed += 1
            self.tests.append({
                'category': self.current_category,
                'name': test_name,
                'status': 'PASSED',
                'duration': duration,
                'error': None
            })
            print(f"  [OK] Passed in {duration:.3f}s")
            return True

        except Exception as e:
            duration = time.time() - start if 'start' in locals() else 0
            error_msg = str(e)
            error_trace = traceback.format_exc()

            self.failed += 1
            self.tests.append({
                'category': self.current_category,
                'name': test_name,
                'status': 'FAILED',
                'duration': duration,
                'error': error_msg,
                'trace': error_trace
            })
            print(f"  [FAIL] {error_msg}")
            print(f"  Traceback: {error_trace}")
            return False

    def test_session_manager(self):
        """Test session management system"""

        def test_import():
            """Test module import"""
            from session_manager import SessionManager
            assert SessionManager is not None

        def test_database_creation():
            """Test database initialization"""
            from session_manager import SessionManager
            test_db = self.models_dir / "test_sessions.db"
            if test_db.exists():
                test_db.unlink()

            sm = SessionManager(test_db)
            assert test_db.exists()

            # Cleanup
            test_db.unlink()

        def test_crud_operations():
            """Test create, read, update, delete operations"""
            from session_manager import SessionManager
            test_db = self.models_dir / "test_sessions.db"
            if test_db.exists():
                test_db.unlink()

            sm = SessionManager(test_db)

            # Create session
            session_id = sm.create_session("test_model", {"test": True})
            assert session_id is not None

            # Add messages
            msg_id = sm.add_message(session_id, "user", "Hello", 10)
            assert msg_id is not None

            # Read session
            session = sm.get_session(session_id)
            assert session is not None
            assert session['model_id'] == "test_model"

            # Update session
            sm.update_session(session_id, title="Test Session")
            session = sm.get_session(session_id)
            assert session['title'] == "Test Session"

            # Delete session
            sm.delete_session(session_id)
            session = sm.get_session(session_id)
            assert session is None

            # Cleanup
            test_db.unlink()

        def test_search_functionality():
            """Test search features"""
            from session_manager import SessionManager
            test_db = self.models_dir / "test_sessions.db"
            if test_db.exists():
                test_db.unlink()

            sm = SessionManager(test_db)

            # Create test sessions
            sid1 = sm.create_session("model1", {"test": True})
            sm.add_message(sid1, "user", "Search test content", 10)

            sid2 = sm.create_session("model2", {"test": True})
            sm.add_message(sid2, "user", "Different content", 10)

            # Search
            results = sm.search_messages("Search test")
            assert len(results) > 0

            # Cleanup
            test_db.unlink()

        self.run_test("Import session_manager", test_import)
        self.run_test("Database creation", test_database_creation)
        self.run_test("CRUD operations", test_crud_operations)
        self.run_test("Search functionality", test_search_functionality)

    def test_response_capture(self):
        """Test response processor for capturing outputs"""

        def test_import():
            """Test module import"""
            from response_processor import ResponseProcessor
            assert ResponseProcessor is not None

        def test_initialization():
            """Test processor initialization"""
            from response_processor import ResponseProcessor
            processor = ResponseProcessor()
            assert processor is not None

        def test_markdown_formatting():
            """Test markdown output formatting"""
            from response_processor import ResponseProcessor
            processor = ResponseProcessor()

            # Test formatting
            result = processor.format_markdown("Test", "model1", 100, 50, 1.5)
            assert "model1" in result
            assert "Test" in result

        self.run_test("Import response_processor", test_import)
        self.run_test("Processor initialization", test_initialization)
        self.run_test("Markdown formatting", test_markdown_formatting)

    def test_prompt_templates(self):
        """Test prompt template system"""

        def test_import():
            """Test module import"""
            from template_manager import TemplateManager, PromptTemplate
            assert TemplateManager is not None
            assert PromptTemplate is not None

        def test_template_loading():
            """Test loading templates from directory"""
            from template_manager import TemplateManager
            templates_dir = self.models_dir / "prompt_templates"

            if not templates_dir.exists():
                # Create test template
                templates_dir.mkdir(exist_ok=True)
                test_template = templates_dir / "test_template.yaml"
                test_template.write_text("""
metadata:
  name: Test Template
  description: Test
  category: test
  variables:
    - name: input_text
      description: Test input

system_prompt: |
  You are a test assistant.

user_prompt: |
  Process: {{ input_text }}
""")

            tm = TemplateManager(templates_dir)
            templates = tm.list_templates()
            assert len(templates) > 0

        def test_variable_substitution():
            """Test template variable rendering"""
            from template_manager import PromptTemplate
            templates_dir = self.models_dir / "prompt_templates"

            if not templates_dir.exists():
                templates_dir.mkdir(exist_ok=True)

            test_template = templates_dir / "test_vars.yaml"
            test_template.write_text("""
metadata:
  name: Variable Test
  variables:
    - name: var1
    - name: var2

user_prompt: |
  {{ var1 }} and {{ var2 }}
""")

            pt = PromptTemplate(test_template)
            rendered = pt.render(var1="Hello", var2="World")
            assert "Hello" in rendered['user_prompt']
            assert "World" in rendered['user_prompt']

        self.run_test("Import template_manager", test_import)
        self.run_test("Template loading", test_template_loading)
        self.run_test("Variable substitution", test_variable_substitution)

    def test_context_management(self):
        """Test context management"""

        def test_import():
            """Test module import"""
            from context_manager import ContextManager
            assert ContextManager is not None

        def test_file_loading():
            """Test loading context from files"""
            from context_manager import ContextManager

            # Create test file
            test_file = self.models_dir / "test_context.txt"
            test_file.write_text("Test context content")

            cm = ContextManager()
            content = cm.load_file(test_file)
            assert "Test context content" in content

            # Cleanup
            test_file.unlink()

        def test_token_estimation():
            """Test token counting"""
            from context_manager import ContextManager
            cm = ContextManager()

            text = "This is a test sentence for token estimation."
            tokens = cm.estimate_tokens(text)
            assert tokens > 0

        def test_context_building():
            """Test building context from multiple sources"""
            from context_manager import ContextManager
            cm = ContextManager()

            # Create test files
            file1 = self.models_dir / "context1.txt"
            file2 = self.models_dir / "context2.txt"
            file1.write_text("Context part 1")
            file2.write_text("Context part 2")

            context = cm.build_context([file1, file2])
            assert "Context part 1" in context
            assert "Context part 2" in context

            # Cleanup
            file1.unlink()
            file2.unlink()

        self.run_test("Import context_manager", test_import)
        self.run_test("File loading", test_file_loading)
        self.run_test("Token estimation", test_token_estimation)
        self.run_test("Context building", test_context_building)

    def test_response_processing(self):
        """Test response post-processing"""

        def test_import():
            """Test module import"""
            from response_processor import ResponseProcessor
            assert ResponseProcessor is not None

        def test_json_extraction():
            """Test JSON extraction from responses"""
            from response_processor import ResponseProcessor
            processor = ResponseProcessor()

            text_with_json = 'Here is data: {"key": "value", "number": 42}'
            extracted = processor.extract_json(text_with_json)
            assert extracted is not None
            assert extracted.get('key') == 'value'

        def test_code_extraction():
            """Test code block extraction"""
            from response_processor import ResponseProcessor
            processor = ResponseProcessor()

            text_with_code = """
Here is some code:
```python
def hello():
    print("Hello")
```
"""
            code_blocks = processor.extract_code_blocks(text_with_code)
            assert len(code_blocks) > 0
            assert "def hello()" in code_blocks[0]

        self.run_test("Import for processing", test_import)
        self.run_test("JSON extraction", test_json_extraction)
        self.run_test("Code extraction", test_code_extraction)

    def test_model_selector(self):
        """Test intelligent model selection"""

        def test_import():
            """Test module import"""
            from model_selector import ModelSelector
            assert ModelSelector is not None

        def test_initialization():
            """Test selector initialization"""
            from model_selector import ModelSelector
            selector = ModelSelector()
            assert selector is not None

        def test_capability_matching():
            """Test matching prompts to model capabilities"""
            from model_selector import ModelSelector
            selector = ModelSelector()

            # Test code-related prompt
            code_prompt = "Write a Python function to sort a list"
            recommended = selector.recommend_model(code_prompt)
            assert recommended is not None

        self.run_test("Import model_selector", test_import)
        self.run_test("Selector initialization", test_initialization)
        self.run_test("Capability matching", test_capability_matching)

    def test_model_comparison(self):
        """Test model comparison (A/B testing)"""

        def test_import():
            """Test module import"""
            from model_comparison import ModelComparison, ComparisonResult
            assert ModelComparison is not None
            assert ComparisonResult is not None

        def test_comparison_creation():
            """Test creating a comparison"""
            from model_comparison import ModelComparison

            results_dir = self.models_dir / "test_comparisons"
            results_dir.mkdir(exist_ok=True)

            mc = ModelComparison(results_dir)
            comparison = mc.create_comparison("Test prompt")
            assert comparison is not None
            assert comparison.prompt == "Test prompt"

            # Cleanup
            import shutil
            shutil.rmtree(results_dir)

        def test_result_storage():
            """Test storing comparison results"""
            from model_comparison import ModelComparison

            results_dir = self.models_dir / "test_comparisons"
            results_dir.mkdir(exist_ok=True)

            mc = ModelComparison(results_dir)
            comparison = mc.create_comparison("Test prompt")

            # Add result
            mc.add_result(comparison, "model1", "Response 1", 100, 50, 1.0)
            mc.save_comparison(comparison)

            # Load and verify
            loaded = mc.load_comparison(comparison.comparison_id)
            assert loaded is not None
            assert len(loaded.responses) == 1

            # Cleanup
            import shutil
            shutil.rmtree(results_dir)

        self.run_test("Import model_comparison", test_import)
        self.run_test("Comparison creation", test_comparison_creation)
        self.run_test("Result storage", test_result_storage)

    def test_batch_processing(self):
        """Test batch processing"""

        def test_import():
            """Test module import"""
            from batch_processor import BatchProcessor, BatchJob, BatchResult
            assert BatchProcessor is not None
            assert BatchJob is not None

        def test_job_creation():
            """Test creating batch job"""
            from batch_processor import BatchProcessor

            checkpoint_dir = self.models_dir / "test_checkpoints"
            checkpoint_dir.mkdir(exist_ok=True)

            bp = BatchProcessor(checkpoint_dir)
            prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
            job = bp.create_job("test_model", prompts)

            assert job is not None
            assert job.total_prompts == 3

            # Cleanup
            import shutil
            shutil.rmtree(checkpoint_dir)

        def test_checkpointing():
            """Test checkpoint save/load"""
            from batch_processor import BatchProcessor

            checkpoint_dir = self.models_dir / "test_checkpoints"
            checkpoint_dir.mkdir(exist_ok=True)

            bp = BatchProcessor(checkpoint_dir)
            prompts = ["Prompt 1", "Prompt 2"]
            job = bp.create_job("test_model", prompts)

            # Save checkpoint
            bp.save_checkpoint(job)

            # Load checkpoint
            loaded_job = bp.load_checkpoint(job.job_id)
            assert loaded_job is not None
            assert loaded_job.job_id == job.job_id

            # Cleanup
            import shutil
            shutil.rmtree(checkpoint_dir)

        self.run_test("Import batch_processor", test_import)
        self.run_test("Job creation", test_job_creation)
        self.run_test("Checkpointing", test_checkpointing)

    def test_analytics(self):
        """Test analytics dashboard"""

        def test_import():
            """Test module import"""
            from analytics_dashboard import AnalyticsDashboard
            assert AnalyticsDashboard is not None

        def test_initialization():
            """Test dashboard with session manager"""
            from session_manager import SessionManager
            from analytics_dashboard import AnalyticsDashboard

            test_db = self.models_dir / "test_analytics.db"
            if test_db.exists():
                test_db.unlink()

            sm = SessionManager(test_db)
            dashboard = AnalyticsDashboard(sm)
            assert dashboard is not None

            # Cleanup
            test_db.unlink()

        def test_usage_stats():
            """Test usage statistics collection"""
            from session_manager import SessionManager
            from analytics_dashboard import AnalyticsDashboard

            test_db = self.models_dir / "test_analytics.db"
            if test_db.exists():
                test_db.unlink()

            sm = SessionManager(test_db)

            # Create test data
            sid = sm.create_session("test_model")
            sm.add_message(sid, "user", "Test", 10)
            sm.add_message(sid, "assistant", "Response", 20)

            dashboard = AnalyticsDashboard(sm)
            stats = dashboard.get_usage_statistics(days=30)

            assert stats['total_sessions'] >= 1
            assert stats['total_messages'] >= 2

            # Cleanup
            test_db.unlink()

        self.run_test("Import analytics_dashboard", test_import)
        self.run_test("Dashboard initialization", test_initialization)
        self.run_test("Usage statistics", test_usage_stats)

    def test_workflows(self):
        """Test workflow engine"""

        def test_import():
            """Test module import"""
            from workflow_engine import WorkflowEngine, WorkflowStep, WorkflowExecution
            assert WorkflowEngine is not None
            assert WorkflowStep is not None

        def test_workflow_loading():
            """Test loading workflow from YAML"""
            from workflow_engine import WorkflowEngine

            workflows_dir = self.models_dir / "test_workflows"
            workflows_dir.mkdir(exist_ok=True)

            # Create test workflow
            test_workflow = workflows_dir / "test_flow.yaml"
            test_workflow.write_text("""
name: Test Workflow
description: Test workflow
variables:
  input_var: default_value

steps:
  - name: step1
    type: prompt
    config:
      prompt: "Process {{ input_var }}"
      model: test_model
""")

            # Mock AI router
            class MockRouter:
                pass

            we = WorkflowEngine(workflows_dir, MockRouter())
            workflows = we.list_workflows()
            assert len(workflows) > 0

            # Cleanup
            import shutil
            shutil.rmtree(workflows_dir)

        def test_variable_passing():
            """Test variable passing between steps"""
            from workflow_engine import WorkflowExecution, WorkflowStep

            step1 = WorkflowStep("step1", "prompt", {"output_var": "result"})
            execution = WorkflowExecution(
                "test_id",
                "test_workflow",
                [step1],
                {"input": "test"},
                {},
                "pending"
            )

            # Set variable
            execution.variables["test_var"] = "test_value"
            assert execution.variables["test_var"] == "test_value"

        self.run_test("Import workflow_engine", test_import)
        self.run_test("Workflow loading", test_workflow_loading)
        self.run_test("Variable passing", test_variable_passing)

    def test_feature_interactions(self):
        """Test features working together"""

        def test_template_with_context():
            """Test using templates with context manager"""
            from template_manager import TemplateManager
            from context_manager import ContextManager

            templates_dir = self.models_dir / "prompt_templates"
            templates_dir.mkdir(exist_ok=True)

            # Create template that uses context
            test_template = templates_dir / "context_template.yaml"
            test_template.write_text("""
metadata:
  name: Context Test
  variables:
    - name: context_data

user_prompt: |
  Use this context: {{ context_data }}
""")

            # Load context
            context_file = self.models_dir / "test_ctx.txt"
            context_file.write_text("Important context")

            cm = ContextManager()
            context = cm.load_file(context_file)

            # Render template with context
            from template_manager import PromptTemplate
            pt = PromptTemplate(test_template)
            rendered = pt.render(context_data=context)

            assert "Important context" in rendered['user_prompt']

            # Cleanup
            context_file.unlink()

        def test_session_with_analytics():
            """Test session manager integration with analytics"""
            from session_manager import SessionManager
            from analytics_dashboard import AnalyticsDashboard

            test_db = self.models_dir / "test_integration.db"
            if test_db.exists():
                test_db.unlink()

            sm = SessionManager(test_db)
            dashboard = AnalyticsDashboard(sm)

            # Create sessions
            sid1 = sm.create_session("model1")
            sm.add_message(sid1, "user", "Q1", 10)
            sm.add_message(sid1, "assistant", "A1", 20)

            sid2 = sm.create_session("model2")
            sm.add_message(sid2, "user", "Q2", 15)

            # Get analytics
            stats = dashboard.get_usage_statistics(days=7)
            model_stats = dashboard.get_model_statistics()

            assert stats['total_sessions'] == 2
            assert len(model_stats) == 2

            # Cleanup
            test_db.unlink()

        def test_batch_with_templates():
            """Test batch processing with templates"""
            from batch_processor import BatchProcessor
            from template_manager import TemplateManager

            # Create batch processor
            checkpoint_dir = self.models_dir / "test_batch_checkpoints"
            checkpoint_dir.mkdir(exist_ok=True)
            bp = BatchProcessor(checkpoint_dir)

            # Create template
            templates_dir = self.models_dir / "prompt_templates"
            templates_dir.mkdir(exist_ok=True)

            # Create prompts using template variables
            prompts = [
                "Process item 1",
                "Process item 2",
                "Process item 3"
            ]

            job = bp.create_job("test_model", prompts)
            assert job.total_prompts == 3

            # Cleanup
            import shutil
            shutil.rmtree(checkpoint_dir)

        self.run_test("Template + Context", test_template_with_context)
        self.run_test("Session + Analytics", test_session_with_analytics)
        self.run_test("Batch + Templates", test_batch_with_templates)

    def print_summary(self):
        """Print test execution summary"""
        total_time = time.time() - self.start_time
        total_tests = self.passed + self.failed

        print()
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed} ({100*self.passed/total_tests if total_tests > 0 else 0:.1f}%)")
        print(f"Failed: {self.failed} ({100*self.failed/total_tests if total_tests > 0 else 0:.1f}%)")
        print(f"Total Time: {total_time:.2f}s")
        print()

        # Category breakdown
        categories = {}
        for test in self.tests:
            cat = test['category']
            if cat not in categories:
                categories[cat] = {'passed': 0, 'failed': 0}

            if test['status'] == 'PASSED':
                categories[cat]['passed'] += 1
            else:
                categories[cat]['failed'] += 1

        print("Category Breakdown:")
        for cat, results in categories.items():
            total = results['passed'] + results['failed']
            print(f"  {cat}: {results['passed']}/{total} passed")

        print()

        # Failed tests detail
        if self.failed > 0:
            print("FAILED TESTS:")
            print("-" * 70)
            for test in self.tests:
                if test['status'] == 'FAILED':
                    print(f"\n{test['category']} :: {test['name']}")
                    print(f"  Error: {test['error']}")

        print()
        print("=" * 70)

        # Save results to JSON
        results_file = self.models_dir / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tests': total_tests,
                'passed': self.passed,
                'failed': self.failed,
                'duration': total_time,
                'tests': self.tests
            }, f, indent=2)

        print(f"Results saved to: {results_file}")

        return self.failed == 0


def main():
    """Main entry point"""
    models_dir = Path(__file__).parent

    suite = IntegrationTestSuite(models_dir)
    success = suite.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
