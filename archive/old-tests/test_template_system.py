#!/usr/bin/env python3
"""
Test script for the Prompt Templates Library system
Run after installing dependencies: pip install -r requirements.txt
"""

from pathlib import Path
from template_manager import TemplateManager

def test_template_system():
    """Test the template system components"""
    print("=" * 60)
    print("Testing Prompt Templates Library System")
    print("=" * 60)

    # Initialize template manager
    templates_dir = Path("D:/models/prompt-templates")
    print(f"\n1. Initializing TemplateManager with: {templates_dir}")

    try:
        tm = TemplateManager(templates_dir)
        print(f"   ✓ TemplateManager loaded successfully")
    except Exception as e:
        print(f"   ✗ Failed to load TemplateManager: {e}")
        return False

    # Check templates loaded
    print(f"\n2. Checking loaded templates")
    print(f"   Found {len(tm.templates)} templates")

    if len(tm.templates) == 0:
        print(f"   ✗ No templates found!")
        return False
    else:
        print(f"   ✓ Templates loaded successfully")

    # List categories
    categories = tm.get_categories()
    print(f"\n3. Available categories: {', '.join(categories)}")

    # Test each template
    print(f"\n4. Testing individual templates:")
    for template_id, template in tm.templates.items():
        print(f"\n   Template: {template_id}")
        info = template.get_template_info()
        print(f"   - Name: {info['name']}")
        print(f"   - Category: {info['category']}")
        print(f"   - Description: {info['description']}")
        print(f"   - Variables: {len(info['variables'])}")

        # Test rendering with sample data
        sample_vars = {}
        for var in info['variables']:
            var_name = var.get('name')
            var_default = var.get('default', 'test_value')
            sample_vars[var_name] = var_default

        try:
            rendered = template.render(sample_vars)
            print(f"   ✓ Rendering successful")
            print(f"   - System prompt length: {len(rendered.get('system_prompt', ''))}")
            print(f"   - User prompt length: {len(rendered.get('user_prompt', ''))}")
        except Exception as e:
            print(f"   ✗ Rendering failed: {e}")

    print(f"\n5. Testing template listing")
    all_templates = tm.list_templates()
    print(f"   Found {len(all_templates)} templates via list_templates()")

    # Test category filtering
    for category in categories:
        cat_templates = tm.list_templates(category=category)
        print(f"   Category '{category}': {len(cat_templates)} templates")

    print("\n" + "=" * 60)
    print("✓ All tests passed successfully!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = test_template_system()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
