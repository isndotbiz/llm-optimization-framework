#!/usr/bin/env python3
"""
Template Manager - YAML + Jinja2 based prompt template system
Provides interactive template selection and rendering for AI Router
"""

import yaml
from jinja2 import Template, Environment, FileSystemLoader, meta
from pathlib import Path
from typing import Dict, List, Optional, Any
import re


class PromptTemplate:
    """Represents a single prompt template with metadata and rendering capability"""

    def __init__(self, template_path: Path):
        """
        Initialize a prompt template from a YAML file

        Args:
            template_path: Path to the YAML template file
        """
        self.template_path = template_path
        self.metadata = {}
        self.system_template = None
        self.user_template = None

        # Load and parse YAML
        self._load_template()

    def _load_template(self):
        """Load and parse the YAML template file"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # Extract metadata
            self.metadata = data.get('metadata', {})

            # Create Jinja2 templates
            system_prompt = data.get('system_prompt', '')
            user_prompt = data.get('user_prompt', '')

            if system_prompt:
                self.system_template = Template(system_prompt)

            if user_prompt:
                self.user_template = Template(user_prompt)

        except Exception as e:
            raise ValueError(f"Failed to load template from {self.template_path}: {e}")

    def render(self, variables: Dict[str, Any]) -> Dict[str, str]:
        """
        Render template with provided variables

        Args:
            variables: Dictionary of variable names to values

        Returns:
            Dictionary with 'system_prompt' and 'user_prompt' keys
        """
        result = {
            'system_prompt': '',
            'user_prompt': ''
        }

        # Apply defaults for missing variables
        filled_variables = self._apply_defaults(variables)

        # Render templates
        if self.system_template:
            result['system_prompt'] = self.system_template.render(**filled_variables)

        if self.user_template:
            result['user_prompt'] = self.user_template.render(**filled_variables)

        return result

    def _apply_defaults(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values for missing variables"""
        filled = variables.copy()

        for var_def in self.metadata.get('variables', []):
            var_name = var_def.get('name')
            if var_name and var_name not in filled:
                if 'default' in var_def:
                    filled[var_name] = var_def['default']

        return filled

    def get_required_variables(self) -> List[Dict[str, Any]]:
        """
        Get list of required variables with descriptions

        Returns:
            List of variable definitions from metadata
        """
        return self.metadata.get('variables', [])

    def get_template_info(self) -> Dict[str, Any]:
        """Get template metadata information"""
        return {
            'name': self.metadata.get('name', 'Unknown'),
            'id': self.metadata.get('id', ''),
            'category': self.metadata.get('category', 'general'),
            'description': self.metadata.get('description', ''),
            'recommended_models': self.metadata.get('recommended_models', []),
            'variables': self.get_required_variables()
        }


class TemplateManager:
    """Manages the prompt template library"""

    def __init__(self, templates_dir: Path):
        """
        Initialize the template manager

        Args:
            templates_dir: Directory containing template YAML files
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True, parents=True)
        self.templates = {}
        self._load_templates()

    def _load_templates(self):
        """Load all template files from the templates directory"""
        self.templates = {}

        # Find all .yaml and .yml files
        for template_file in self.templates_dir.glob('*.yaml'):
            try:
                template = PromptTemplate(template_file)
                template_id = template.metadata.get('id', template_file.stem)
                self.templates[template_id] = template
            except Exception as e:
                print(f"Warning: Failed to load template {template_file.name}: {e}")

        for template_file in self.templates_dir.glob('*.yml'):
            try:
                template = PromptTemplate(template_file)
                template_id = template.metadata.get('id', template_file.stem)
                self.templates[template_id] = template
            except Exception as e:
                print(f"Warning: Failed to load template {template_file.name}: {e}")

    def list_templates(self, category: Optional[str] = None) -> List[Dict]:
        """
        List available templates, optionally filtered by category

        Args:
            category: Optional category filter

        Returns:
            List of template info dictionaries
        """
        result = []

        for template_id, template in self.templates.items():
            info = template.get_template_info()

            # Filter by category if specified
            if category is None or info.get('category') == category:
                result.append(info)

        return result

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        Load specific template by ID

        Args:
            template_id: The template identifier

        Returns:
            PromptTemplate object or None if not found
        """
        return self.templates.get(template_id)

    def get_categories(self) -> List[str]:
        """
        Get list of all available template categories

        Returns:
            Sorted list of unique categories
        """
        categories = set()
        for template in self.templates.values():
            category = template.metadata.get('category', 'general')
            categories.add(category)

        return sorted(list(categories))

    def create_template_interactive(self) -> Optional[Path]:
        """
        Interactive template creation wizard

        Returns:
            Path to created template file or None if cancelled
        """
        print("\nTemplate Creation Wizard")
        print("=" * 60)

        # Get template metadata
        print("\nTemplate Metadata:")
        name = input("Template name: ").strip()
        if not name:
            print("Template creation cancelled.")
            return None

        template_id = input("Template ID (lowercase, no spaces): ").strip()
        if not template_id:
            template_id = name.lower().replace(' ', '_')

        category = input("Category (coding/creative/research/general): ").strip()
        if not category:
            category = "general"

        description = input("Description: ").strip()

        # Get variables
        print("\nTemplate Variables:")
        print("Enter variable definitions (press Enter with empty name to finish)")
        variables = []

        while True:
            var_name = input("  Variable name: ").strip()
            if not var_name:
                break

            var_desc = input("  Description: ").strip()
            var_required = input("  Required? (y/n): ").strip().lower() == 'y'
            var_default = input("  Default value (optional): ").strip()

            var_def = {
                'name': var_name,
                'description': var_desc,
                'required': var_required
            }

            if var_default:
                var_def['default'] = var_default

            variables.append(var_def)

        # Get prompts
        print("\nTemplate Prompts:")
        print("Enter system prompt (press Ctrl+D or Ctrl+Z when done):")
        system_lines = []
        try:
            while True:
                line = input()
                system_lines.append(line)
        except EOFError:
            pass

        system_prompt = '\n'.join(system_lines)

        print("\nEnter user prompt template (press Ctrl+D or Ctrl+Z when done):")
        user_lines = []
        try:
            while True:
                line = input()
                user_lines.append(line)
        except EOFError:
            pass

        user_prompt = '\n'.join(user_lines)

        # Build template structure
        template_data = {
            'metadata': {
                'name': name,
                'id': template_id,
                'category': category,
                'description': description,
                'variables': variables
            },
            'system_prompt': system_prompt,
            'user_prompt': user_prompt
        }

        # Save template
        template_path = self.templates_dir / f"{template_id}.yaml"
        with open(template_path, 'w', encoding='utf-8') as f:
            yaml.dump(template_data, f, default_flow_style=False, sort_keys=False)

        print(f"\nTemplate created successfully: {template_path}")

        # Reload templates
        self._load_templates()

        return template_path
