# Context Management - Quick Start Guide

## How to Use Context Management in AI Router

### Step 1: Launch AI Router
```bash
python ai-router.py
```

### Step 2: Select Context Management
From the main menu, choose option **[3] Context Management**

### Step 3: Add Context

#### Option A: Add Files
1. Select **[1] Add file(s) to context**
2. Enter file path (absolute or relative to D:\models)
3. Press Enter on empty line when done
4. Files are loaded with automatic token estimation

**Example**:
```
File path: context_manager.py
File path: README.md
File path: [press Enter]
```

#### Option B: Add Text
1. Select **[2] Add text to context**
2. Enter a label for your text
3. Type or paste your text content
4. Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done

### Step 4: Review Context
The menu shows:
- All loaded context items with icons (📄 for files, 📝 for text)
- Token count per item
- Total tokens and utilization percentage

### Step 5: Execute with Context
1. Select **[6] Execute with context**
2. Enter your prompt/question
3. System builds full prompt with context automatically
4. Model is recommended based on your query
5. Confirm to run the model

---

## Features Overview

### Token Management
- **Default limit**: 4,096 tokens
- **Adjust limit**: Option [5] Set token limit
- **Auto-truncation**: System prevents overflow

### Context Operations
- **Add files**: Option [1]
- **Add text**: Option [2]
- **Remove item**: Option [3]
- **Clear all**: Option [4]
- **Set limit**: Option [5]
- **Execute**: Option [6]

---

## Example Workflow

### Scenario: Code Review with Context

1. Launch ai-router.py
2. Select [3] Context Management
3. Add files:
   - `src/main.py`
   - `tests/test_main.py`
   - `README.md`
4. Select [6] Execute with context
5. Prompt: "Review this code for bugs and suggest improvements"
6. System loads all files, builds context, recommends model
7. Model analyzes with full context awareness

---

## Tips

1. **Relative Paths**: Paths are resolved relative to D:\models
2. **Token Awareness**: Watch utilization percentage to avoid truncation
3. **Context Reuse**: Context persists within the session until cleared
4. **File Types**: Supports 30+ programming languages with auto-detection
5. **Large Files**: System warns if approaching token limits

---

## Context Templates

Pre-built templates available in: `D:\models\context-templates\`

- `code_analysis.yaml` - For code review tasks
- `debugging_assistant.yaml` - For debugging help
- `documentation_writer.yaml` - For doc generation

---

## Troubleshooting

**Q: File not found error?**
- Check path is correct
- Use absolute path or relative to D:\models
- Verify file exists

**Q: Token limit exceeded?**
- Increase limit with option [5]
- Remove some context items with option [3]
- Or clear and re-add with option [4]

**Q: Context not included in prompt?**
- Verify context shows in menu (should see 📄 or 📝 icons)
- Check token count > 0
- Ensure using option [6] Execute with context

---

## Quick Reference Commands

```
Main Menu > [3] Context Management

Context Menu Options:
[1] Add file(s) to context
[2] Add text to context
[3] Remove context item
[4] Clear all context
[5] Set token limit
[6] Execute with context
[0] Return to main menu
```

---

**Status**: Ready to use
**Location**: D:\models\ai-router.py
**Documentation**: CONTEXT_INTEGRATION_SUMMARY.md
