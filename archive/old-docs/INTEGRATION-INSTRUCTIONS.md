# Context Management System - Integration Instructions

## Current Status

✓ **Completed**:
1. ContextManager class created (`context_manager.py`)
2. Context templates created (3 YAML files)
3. Test suite created and passing (`test_context_manager.py`)
4. Documentation created (`CONTEXT-MANAGEMENT-GUIDE.md`)
5. Integration code prepared (`context_integration.py`)
6. Import and initialization added to `ai-router.py`
7. Main menu updated with Context Management option [3]

⚠ **Remaining**:
1. Add context management methods to AIRouter class

## Integration Steps

### Step 1: Import Verification

Check that `ai-router.py` has the import (line ~21):
```python
from context_manager import ContextManager
```

Status: ✓ **Already added**

### Step 2: Initialization Verification

Check that `AIRouter.__init__()` has (line ~402):
```python
# Initialize context manager
self.context_manager = ContextManager()
```

Status: ✓ **Already added**

### Step 3: Menu Verification

Check that interactive_mode() has updated menu (line ~571-582):
```python
print(f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET} 🎯 Auto-select model based on prompt")
print(f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET} 📋 Browse & select from all models")
print(f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET} 📎 Context Management (Load files/text)")  # NEW
print(f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET} 💬 View system prompt examples")
...
print(f"{Colors.BRIGHT_GREEN}[8]{Colors.RESET} 🚪 Exit")  # Changed from [7]
```

Status: ✓ **Already added**

### Step 4: Menu Handler Verification

Check that choice handler has (line ~595-596):
```python
elif choice == "3":
    self.context_mode()  # NEW
```

Status: ✓ **Already added**

### Step 5: Add Context Methods

**Copy the following 6 methods from `context_integration.py` to `ai-router.py`:**

Insert them **before** the `view_documentation()` method (around line 880).

#### Methods to Add:

1. **context_mode()** - Main context management menu
2. **add_files_to_context()** - Interactive file addition
3. **add_text_to_context()** - Interactive text addition
4. **remove_context_item()** - Remove specific items
5. **set_token_limit()** - Adjust token limits
6. **execute_with_context()** - Run models with context

#### Quick Copy-Paste:

Open `context_integration.py` and copy all 6 method definitions (they're complete and ready to paste).

Insert location in `ai-router.py`:
```python
# Around line 880, BEFORE this line:
def view_documentation(self):
    """Display documentation guide menu"""
```

## Testing After Integration

### Test 1: Basic Menu Access

```bash
python ai-router.py
```

Expected:
- Main menu shows option [3] Context Management
- Selecting [3] opens context submenu

### Test 2: Add a File

```
Main Menu > [3] Context Management
Context Menu > [1] Add file(s) to context
File path: context_manager.py
File path: [Enter]
```

Expected:
- File loads successfully
- Shows token count
- Returns to context menu

### Test 3: Execute with Context

```
Context Menu > [6] Execute with context
Prompt: Analyze this file
```

Expected:
- Shows prompt preview
- Detects use case
- Recommends model
- Asks to execute

### Test 4: Context Summary

```
Context Menu (with files loaded)
```

Expected:
- Shows all loaded files/text
- Displays token counts
- Shows utilization percentage

## Verification Checklist

After integration, verify:

- [ ] Import statement present in ai-router.py
- [ ] ContextManager initialized in __init__
- [ ] Menu option [3] exists
- [ ] Menu handler calls context_mode()
- [ ] All 6 methods added to AIRouter class
- [ ] No syntax errors (run `python ai-router.py --help`)
- [ ] Context menu accessible (run and select [3])
- [ ] Can add files successfully
- [ ] Can add text successfully
- [ ] Can execute with context
- [ ] Token counting works
- [ ] Context clears properly

## Files Reference

### Core Files
- `D:\models\context_manager.py` - ContextManager class
- `D:\models\ai-router.py` - AI Router main file (needs integration)
- `D:\models\context_integration.py` - Methods to copy from

### Templates
- `D:\models\context-templates\code_analysis.yaml`
- `D:\models\context-templates\documentation_writer.yaml`
- `D:\models\context-templates\debugging_assistant.yaml`

### Documentation
- `D:\models\CONTEXT-MANAGEMENT-GUIDE.md` - User guide
- `D:\models\CONTEXT-SYSTEM-IMPLEMENTATION.md` - Implementation summary
- `D:\models\INTEGRATION-INSTRUCTIONS.md` - This file

### Testing
- `D:\models\test_context_manager.py` - Test suite (runs independently)

## Troubleshooting

### Problem: Import Error
```
ImportError: No module named 'context_manager'
```

**Solution**: Ensure `context_manager.py` is in the same directory as `ai-router.py`

### Problem: Method Not Found
```
AttributeError: 'AIRouter' object has no attribute 'context_mode'
```

**Solution**: Add the 6 methods from `context_integration.py`

### Problem: Colors Not Defined
```
NameError: name 'Colors' is not defined
```

**Solution**: Methods must be inside the AIRouter class (indented properly)

### Problem: Path Not Found
```
FileNotFoundError: No such file or directory
```

**Solution**: Use absolute paths or paths relative to D:\models\

## Next Steps After Integration

1. **Test the integration** with the verification checklist above
2. **Read the user guide**: `CONTEXT-MANAGEMENT-GUIDE.md`
3. **Try the examples** in the guide
4. **Provide feedback** on any issues or improvements

## Questions?

See:
- **User Guide**: `CONTEXT-MANAGEMENT-GUIDE.md`
- **Implementation Details**: `CONTEXT-SYSTEM-IMPLEMENTATION.md`
- **Source Code**: `context_manager.py`
- **Test Examples**: `test_context_manager.py`
