#!/usr/bin/env python3
"""
Workflow Engine Integration Tests
Comprehensive testing for workflow system
"""

import sys
from pathlib import Path
import unittest
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow_engine import WorkflowEngine, WorkflowStep, WorkflowExecution


class MockAIRouter:
    """Mock AI Router for testing"""

    def __init__(self):
        self.calls = []

    def execute_prompt(self, model_id: str, prompt: str, **kwargs):
        """Mock execute prompt"""
        self.calls.append({
            'model_id': model_id,
            'prompt': prompt,
            'kwargs': kwargs
        })
        return f"Mock response for: {prompt}"


class TestWorkflowEngineIntegration(unittest.TestCase):
    """Integration tests for WorkflowEngine"""

    def setUp(self):
        """Set up test workflows directory"""
        self.workflows_dir = Path(__file__).parent.parent / "test_workflows"
        self.workflows_dir.mkdir(exist_ok=True)
        self.mock_router = MockAIRouter()
        self.we = WorkflowEngine(self.workflows_dir, self.mock_router)

    def tearDown(self):
        """Clean up test workflows"""
        if self.workflows_dir.exists():
            shutil.rmtree(self.workflows_dir)

    def create_test_workflow(self, filename: str, content: str):
        """Helper to create test workflow file"""
        workflow_file = self.workflows_dir / filename
        workflow_file.write_text(content)
        return workflow_file

    def test_load_workflow(self):
        """Test loading workflow from YAML"""
        self.create_test_workflow("test_flow.yaml", """
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

        workflows = self.we.list_workflows()
        self.assertEqual(len(workflows), 1)
        self.assertEqual(workflows[0]['name'], 'Test Workflow')

    def test_simple_workflow_execution(self):
        """Test executing simple workflow"""
        self.create_test_workflow("simple.yaml", """
name: Simple Workflow
description: Simple test

variables:
  topic: Python

steps:
  - name: step1
    type: prompt
    config:
      prompt: "Explain {{ topic }}"
      model: test_model
""")

        execution = self.we.execute_workflow("simple.yaml")

        self.assertEqual(execution.status, "completed")
        self.assertIn("step1", execution.results)

    def test_multi_step_workflow(self):
        """Test multi-step workflow"""
        self.create_test_workflow("multi_step.yaml", """
name: Multi-Step Workflow
description: Multiple steps

variables:
  topic: Python

steps:
  - name: step1
    type: prompt
    config:
      prompt: "What is {{ topic }}?"
      model: test_model
      output_var: definition

  - name: step2
    type: prompt
    config:
      prompt: "Explain more about: {{ definition }}"
      model: test_model
    depends_on:
      - step1
""")

        execution = self.we.execute_workflow("multi_step.yaml")

        self.assertEqual(execution.status, "completed")
        self.assertIn("step1", execution.results)
        self.assertIn("step2", execution.results)

    def test_variable_passing(self):
        """Test variable passing between steps"""
        self.create_test_workflow("variable_pass.yaml", """
name: Variable Passing
description: Test variable passing

variables:
  input: test_input

steps:
  - name: extract
    type: prompt
    config:
      prompt: "Process {{ input }}"
      model: test_model
      output_var: extracted

  - name: use_extracted
    type: prompt
    config:
      prompt: "Use {{ extracted }}"
      model: test_model
    depends_on:
      - extract
""")

        execution = self.we.execute_workflow("variable_pass.yaml")

        self.assertIn("extracted", execution.variables)
        self.assertEqual(execution.status, "completed")

    def test_conditional_execution(self):
        """Test conditional step execution"""
        self.create_test_workflow("conditional.yaml", """
name: Conditional Workflow
description: Test conditional execution

variables:
  run_optional: false

steps:
  - name: required_step
    type: prompt
    config:
      prompt: "Always run"
      model: test_model

  - name: optional_step
    type: conditional
    config:
      condition: "{{ run_optional }}"
      then:
        type: prompt
        config:
          prompt: "Optional"
          model: test_model
""")

        execution = self.we.execute_workflow("conditional.yaml")

        self.assertIn("required_step", execution.results)

    def test_workflow_with_loop(self):
        """Test workflow with loop"""
        self.create_test_workflow("loop.yaml", """
name: Loop Workflow
description: Test loop execution

variables:
  items:
    - item1
    - item2
    - item3

steps:
  - name: process_items
    type: loop
    config:
      iterate_over: "{{ items }}"
      loop_var: item
      steps:
        - name: process_one
          type: prompt
          config:
            prompt: "Process {{ item }}"
            model: test_model
""")

        execution = self.we.execute_workflow("loop.yaml")

        self.assertEqual(execution.status, "completed")

    def test_error_handling(self):
        """Test error handling in workflows"""
        self.create_test_workflow("error_handling.yaml", """
name: Error Handling
description: Test error handling

variables:
  input: test

steps:
  - name: may_fail
    type: prompt
    config:
      prompt: "{{ input }}"
      model: test_model
    error_handling:
      on_error: continue
      fallback_value: "Error occurred"

  - name: next_step
    type: prompt
    config:
      prompt: "Continue after error"
      model: test_model
""")

        execution = self.we.execute_workflow("error_handling.yaml")

        # Should complete despite errors
        self.assertIsNotNone(execution)

    def test_workflow_dependencies(self):
        """Test step dependencies"""
        self.create_test_workflow("dependencies.yaml", """
name: Dependencies Test
description: Test step dependencies

steps:
  - name: step_a
    type: prompt
    config:
      prompt: "Step A"
      model: test_model

  - name: step_b
    type: prompt
    config:
      prompt: "Step B"
      model: test_model

  - name: step_c
    type: prompt
    config:
      prompt: "Step C needs A and B"
      model: test_model
    depends_on:
      - step_a
      - step_b
""")

        execution = self.we.execute_workflow("dependencies.yaml")

        # Verify all steps executed
        self.assertIn("step_a", execution.results)
        self.assertIn("step_b", execution.results)
        self.assertIn("step_c", execution.results)

    def test_workflow_validation(self):
        """Test workflow validation"""
        # Invalid workflow (missing required fields)
        self.create_test_workflow("invalid.yaml", """
name: Invalid Workflow
# Missing steps
""")

        with self.assertRaises(Exception):
            self.we.execute_workflow("invalid.yaml")

    def test_save_and_load_execution(self):
        """Test saving and loading workflow execution state"""
        self.create_test_workflow("saveable.yaml", """
name: Saveable Workflow
description: Test save/load

steps:
  - name: step1
    type: prompt
    config:
      prompt: "Test"
      model: test_model
""")

        execution = self.we.execute_workflow("saveable.yaml")

        # Save execution state
        self.we.save_execution(execution)

        # Load execution state
        loaded = self.we.load_execution(execution.workflow_id)

        self.assertEqual(loaded.workflow_id, execution.workflow_id)
        self.assertEqual(loaded.status, execution.status)


if __name__ == "__main__":
    unittest.main()
