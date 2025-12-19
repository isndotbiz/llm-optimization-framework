# Template System Integration Instructions

## Files Created

1. **D:\models\template_manager.py** - Complete TemplateManager class with PromptTemplate
2. **D:\models\prompt-templates\** - Directory containing 5 example templates:
   - code_review.yaml
   - explain_code.yaml
   - creative_story.yaml
   - research_summary.yaml
   - general_assistant.yaml
3. **D:\models\template_mode_method.py** - The template_mode() method to add to AIRouter class

## Integration Steps

### Step 1: Import Added (ALREADY DONE)
The import for TemplateManager has been added to ai-router.py:
```python
from template_manager import TemplateManager
```

### Step 2: Initialize Template Manager (ALREADY DONE)
In AIRouter.__init__(), the template manager has been initialized:
```python
# Initialize template manager
templates_dir = self.models_dir / "prompt-templates"
self.template_manager = TemplateManager(templates_dir)
```

### Step 3: Add template_mode Method
Copy the method from **template_mode_method.py** and add it to the AIRouter class,
just before the `def main():` function (around line 1024 in ai-router.py).

### Step 4: Update Interactive Menu
Update the `interactive_mode()` method to add the Template mode option.

**Current menu (lines 581-599):**
```python
print(f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET} 🎯 Auto-select model based on prompt")
print(f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET} 📋 Browse & select from all models")
print(f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET} 📎 Context Management (Load files/text)")
print(f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET} 💬 View system prompt examples")
print(f"{Colors.BRIGHT_GREEN}[5]{Colors.RESET} ⚙️ View optimal parameters guide")
print(f"{Colors.BRIGHT_GREEN}[6]{Colors.RESET} 📚 View documentation guides")

bypass_status = f"{Colors.BRIGHT_GREEN}ON{Colors.RESET}" if self.bypass_mode else f"{Colors.BRIGHT_RED}OFF{Colors.RESET}"
print(f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET} 🔓 Toggle Auto-Yes Mode (Currently: {bypass_status})")

print(f"{Colors.BRIGHT_GREEN}[8]{Colors.RESET} 🚪 Exit")
```

**Updated menu (add Template Library option):**
```python
print(f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET} 🎯 Auto-select model based on prompt")
print(f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET} 📋 Browse & select from all models")
print(f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET} 📎 Context Management (Load files/text)")
print(f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET} 📝 Prompt Templates Library")  # NEW
print(f"{Colors.BRIGHT_GREEN}[5]{Colors.RESET} 💬 View system prompt examples")
print(f"{Colors.BRIGHT_GREEN}[6]{Colors.RESET} ⚙️ View optimal parameters guide")
print(f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET} 📚 View documentation guides")

bypass_status = f"{Colors.BRIGHT_GREEN}ON{Colors.RESET}" if self.bypass_mode else f"{Colors.BRIGHT_RED}OFF{Colors.RESET}"
print(f"{Colors.BRIGHT_GREEN}[8]{Colors.RESET} 🔓 Toggle Auto-Yes Mode (Currently: {bypass_status})")

print(f"{Colors.BRIGHT_GREEN}[9]{Colors.RESET} 🚪 Exit")
```

Also update the prompt line from:
```python
choice = input(f"\n{Colors.BRIGHT_YELLOW}Enter choice [1-8]: {Colors.RESET}").strip()
```

To:
```python
choice = input(f"\n{Colors.BRIGHT_YELLOW}Enter choice [1-9]: {Colors.RESET}").strip()
```

**Update the menu handler (lines 601-619):**
```python
if choice == "1":
    self.auto_select_mode()
elif choice == "2":
    self.list_models()
elif choice == "3":
    self.context_mode()
elif choice == "4":
    self.template_mode()  # NEW
elif choice == "5":
    self.view_system_prompts()
elif choice == "6":
    self.view_parameters_guide()
elif choice == "7":
    self.view_documentation()
elif choice == "8":
    self.toggle_bypass_mode()
elif choice == "9":
    print(f"\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\n")
    sys.exit(0)
else:
    print(f"{Colors.BRIGHT_RED}Invalid choice. Please try again.{Colors.RESET}")
```

## Quick Integration Script

You can manually perform the edits, or use this sed/awk approach to update the menu:

1. Add the template_mode method from template_mode_method.py before `def main():`
2. Renumber menu items 4-8 to 5-9
3. Insert new menu item 4 for Template Library
4. Update choice handler to call self.template_mode() for choice "4"
5. Shift all other choice handlers down by 1

## Testing

After integration, test by running:
```bash
python ai-router.py
```

Select option [4] to access the Template Library.
