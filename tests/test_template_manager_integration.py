#!/usr/bin/env python3
"""
Template Manager Integration Tests
Comprehensive testing for template system
"""

import sys
from pathlib import Path
import unittest
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from template_manager import TemplateManager, PromptTemplate


class TestTemplateManagerIntegration(unittest.TestCase):
    """Integration tests for TemplateManager"""

    def setUp(self):
        """Set up test templates directory"""
        self.templates_dir = Path(__file__).parent.parent / "test_templates"
        self.templates_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test templates"""
        if self.templates_dir.exists():
            shutil.rmtree(self.templates_dir)

    def create_test_template(self, filename: str, content: str):
        """Helper to create test template file"""
        template_file = self.templates_dir / filename
        template_file.write_text(content)
        return template_file

    def test_load_templates(self):
        """Test loading multiple templates"""
        self.create_test_template("template1.yaml", """
metadata:
  name: Template 1
  description: First test template
  category: test

user_prompt: |
  Test prompt 1
""")

        self.create_test_template("template2.yaml", """
metadata:
  name: Template 2
  description: Second test template
  category: test

user_prompt: |
  Test prompt 2
""")

        tm = TemplateManager(self.templates_dir)
        templates = tm.list_templates()

        self.assertEqual(len(templates), 2)

    def test_template_with_variables(self):
        """Test template variable substitution"""
        template_file = self.create_test_template("vars.yaml", """
metadata:
  name: Variable Test
  variables:
    - name: topic
      description: Topic to discuss
    - name: detail_level
      description: Level of detail

user_prompt: |
  Explain {{ topic }} with {{ detail_level }} detail.
""")

        pt = PromptTemplate(template_file)
        rendered = pt.render(topic="Python", detail_level="high")

        self.assertIn("Python", rendered['user_prompt'])
        self.assertIn("high", rendered['user_prompt'])

    def test_system_and_user_prompts(self):
        """Test templates with both system and user prompts"""
        template_file = self.create_test_template("full.yaml", """
metadata:
  name: Full Template
  category: test

system_prompt: |
  You are a helpful assistant specialized in {{ domain }}.

user_prompt: |
  Help me with {{ task }}.
""")

        pt = PromptTemplate(template_file)
        rendered = pt.render(domain="programming", task="debugging")

        self.assertIn("programming", rendered['system_prompt'])
        self.assertIn("debugging", rendered['user_prompt'])

    def test_filter_by_category(self):
        """Test filtering templates by category"""
        self.create_test_template("code1.yaml", """
metadata:
  name: Code Template 1
  category: coding

user_prompt: |
  Write code
""")

        self.create_test_template("writing1.yaml", """
metadata:
  name: Writing Template 1
  category: writing

user_prompt: |
  Write text
""")

        tm = TemplateManager(self.templates_dir)

        # Filter by coding category
        coding_templates = [t for t in tm.list_templates()
                           if t.get('category') == 'coding']

        self.assertEqual(len(coding_templates), 1)
        self.assertEqual(coding_templates[0]['name'], 'Code Template 1')

    def test_complex_variable_substitution(self):
        """Test complex Jinja2 features"""
        template_file = self.create_test_template("complex.yaml", """
metadata:
  name: Complex Template
  variables:
    - name: items
    - name: action

user_prompt: |
  {% for item in items %}
  - {{ action }} {{ item }}
  {% endfor %}
""")

        pt = PromptTemplate(template_file)
        rendered = pt.render(
            items=["file1.py", "file2.py", "file3.py"],
            action="Process"
        )

        self.assertIn("Process file1.py", rendered['user_prompt'])
        self.assertIn("Process file2.py", rendered['user_prompt'])

    def test_template_metadata_extraction(self):
        """Test extracting template metadata"""
        template_file = self.create_test_template("meta.yaml", """
metadata:
  name: Metadata Test
  description: Test metadata extraction
  category: testing
  author: Test Suite
  version: "1.0"
  tags:
    - test
    - example

user_prompt: |
  Test
""")

        pt = PromptTemplate(template_file)

        self.assertEqual(pt.metadata['name'], 'Metadata Test')
        self.assertEqual(pt.metadata['category'], 'testing')
        self.assertEqual(pt.metadata['author'], 'Test Suite')
        self.assertIn('test', pt.metadata['tags'])

    def test_required_variables(self):
        """Test handling of required vs optional variables"""
        template_file = self.create_test_template("required.yaml", """
metadata:
  name: Required Variables
  variables:
    - name: required_var
      required: true
    - name: optional_var
      required: false
      default: "default_value"

user_prompt: |
  Required: {{ required_var }}
  Optional: {{ optional_var }}
""")

        pt = PromptTemplate(template_file)

        # Render with only required variable
        rendered = pt.render(required_var="provided")

        self.assertIn("provided", rendered['user_prompt'])

    def test_template_validation(self):
        """Test template validation"""
        # Invalid YAML should fail to load
        invalid_file = self.create_test_template("invalid.yaml", """
metadata:
  name: Invalid
invalid yaml content: [[[
""")

        with self.assertRaises(Exception):
            pt = PromptTemplate(invalid_file)

    def test_get_required_variables(self):
        """Test extracting required variables from template"""
        template_file = self.create_test_template("vars_list.yaml", """
metadata:
  name: Variables List
  variables:
    - name: var1
      description: First variable
    - name: var2
      description: Second variable
    - name: var3
      description: Third variable

user_prompt: |
  {{ var1 }} {{ var2 }} {{ var3 }}
""")

        pt = PromptTemplate(template_file)
        variables = pt.get_required_variables()

        self.assertEqual(len(variables), 3)
        self.assertIn('var1', [v['name'] for v in variables])

    def test_conditional_content(self):
        """Test conditional template content"""
        template_file = self.create_test_template("conditional.yaml", """
metadata:
  name: Conditional Template
  variables:
    - name: include_examples
    - name: topic

user_prompt: |
  Explain {{ topic }}.

  {% if include_examples %}
  Please provide examples.
  {% endif %}
""")

        pt = PromptTemplate(template_file)

        # With examples
        rendered1 = pt.render(topic="Python", include_examples=True)
        self.assertIn("provide examples", rendered1['user_prompt'])

        # Without examples
        rendered2 = pt.render(topic="Python", include_examples=False)
        self.assertNotIn("provide examples", rendered2['user_prompt'])


if __name__ == "__main__":
    unittest.main()
