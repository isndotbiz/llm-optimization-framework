# Prompt Templates Library - Quick Start Guide

## What is it?

The Prompt Templates Library is a YAML + Jinja2 based system that allows you to:
- Create reusable prompt templates with variables
- Organize templates by category (coding, creative, research, general)
- Automatically recommend the best model for each template
- Fill in variables interactively
- Preview rendered prompts before execution

## Installation (2 steps)

### Step 1: Install Dependencies
```bash
cd D:\models
pip install -r requirements.txt
```

This installs:
- PyYAML (for template loading)
- Jinja2 (for template rendering)

### Step 2: Verify Installation
```bash
python test_template_system.py
```

You should see:
```
✓ All tests passed successfully!
```

## Usage

### Running AI Router with Templates
```bash
python ai-router.py
```

From the main menu, select:
```
[4] Prompt Templates Library
```

(Note: Option 4 needs to be added to the menu - see integration instructions below)

### Example Workflow

1. **Select category**: Choose from coding, creative, research, or general
2. **Pick a template**: Browse available templates in that category
3. **Fill variables**: Enter values for template variables
4. **Preview**: See the rendered prompt
5. **Execute**: Run with recommended model

## Example: Using Code Review Template

```
[4] Prompt Templates Library
  → [1] Coding (2 templates)
    → [1] Code Review Assistant

code (The code to review):
def calc(x):
    return x * 2

language (Programming language) [python]:
focus (Specific areas to focus on) [all aspects]: performance

[Preview shown]

Run this template with recommended model? [Y/n]: y
```

## Quick Integration (Required)

The system is built but needs final integration into ai-router.py:

### Option A: Manual Integration (Recommended)
Follow the detailed steps in **TEMPLATE_INTEGRATION_INSTRUCTIONS.md**

### Option B: Quick Integration
1. Copy `template_mode()` method from **template_mode_method.py**
2. Paste it into AIRouter class before `def main():`
3. Add menu option [4] for templates
4. Update choice handler

See **TEMPLATE_INTEGRATION_INSTRUCTIONS.md** for exact line numbers and code.

## Available Templates

### 1. Code Review (coding)
Review code for bugs, security, and improvements
- Variables: code, language, focus

### 2. Explain Code (coding)
Explain how code works step-by-step
- Variables: code, language, expertise_level

### 3. Creative Story (creative)
Generate creative stories
- Variables: genre, theme, length, tone

### 4. Research Summary (research)
Comprehensive research analysis
- Variables: topic, depth, format, focus_areas

### 5. General Assistant (general)
Flexible general-purpose assistant
- Variables: query, context, response_style

## Creating New Templates

### Method 1: Copy Existing Template
```bash
cd D:\models\prompt-templates
cp code_review.yaml my_template.yaml
# Edit my_template.yaml
```

### Method 2: Use Template Wizard
```python
from template_manager import TemplateManager
from pathlib import Path

tm = TemplateManager(Path("D:/models/prompt-templates"))
tm.create_template_interactive()
```

## Template Format

```yaml
metadata:
  name: "Your Template Name"
  id: "your_template_v1"
  category: "coding"  # or creative, research, general
  description: "What this template does"
  variables:
    - name: "var1"
      description: "Description"
      required: true
      default: "optional_default"
  recommended_models:
    - qwen3-coder-30b

system_prompt: |
  You are {{var1}}...

user_prompt: |
  Do something with {{var1}}...
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'yaml'"
Install dependencies:
```bash
pip install -r requirements.txt
```

### "No templates found"
Check that templates exist:
```bash
ls D:\models\prompt-templates\*.yaml
```

### Template not loading
Verify YAML syntax:
```bash
python -c "import yaml; yaml.safe_load(open('prompt-templates/your_template.yaml'))"
```

## Files Overview

| File | Purpose |
|------|---------|
| `template_manager.py` | Core template system |
| `prompt-templates/*.yaml` | Template files |
| `template_mode_method.py` | Method to add to AIRouter |
| `requirements.txt` | Dependencies |
| `test_template_system.py` | Test script |
| `TEMPLATE_INTEGRATION_INSTRUCTIONS.md` | Integration guide |
| `TEMPLATE_SYSTEM_SUMMARY.md` | Complete documentation |

## Next Steps

1. ✓ Install dependencies (`pip install -r requirements.txt`)
2. ✓ Test system (`python test_template_system.py`)
3. ⚠ Integrate into ai-router.py (see TEMPLATE_INTEGRATION_INSTRUCTIONS.md)
4. ⚠ Run AI Router and test template mode
5. ⚠ Create your own custom templates

## Support

For detailed information:
- Integration: **TEMPLATE_INTEGRATION_INSTRUCTIONS.md**
- Full documentation: **TEMPLATE_SYSTEM_SUMMARY.md**
- Test the system: `python test_template_system.py`

## Summary

The Prompt Templates Library provides a powerful, flexible way to create and manage reusable prompts. With 5 example templates included, you can start using it immediately after installing dependencies and completing the integration steps.
