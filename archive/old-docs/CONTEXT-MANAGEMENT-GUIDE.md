# Context Management & Injection System

## Overview

The Context Management & Injection system allows you to load files and text as context before sending prompts to AI models. This is essential for:

- **Code Analysis**: Load source files for review, debugging, or refactoring
- **Documentation Generation**: Provide code files to generate comprehensive docs
- **Multi-file Projects**: Analyze relationships between multiple files
- **Technical Writing**: Include technical specs, requirements, or examples

## Quick Start

### 1. Access Context Mode

From the AI Router main menu:
```
[3] Context Management (Load files/text)
```

### 2. Add Files

```
[1] Add file(s) to context
```

Enter file paths (absolute or relative):
```
File path: D:\models\context_manager.py
File path: D:\models\ai-router.py
File path: [press Enter to finish]
```

### 3. Execute with Context

```
[6] Execute with context
```

Enter your prompt:
```
> Analyze these files and suggest improvements
```

The system will:
- Inject all loaded files as context
- Automatically select the best model
- Run the model with the enhanced prompt

## Features

### Token Management

- **Automatic Estimation**: Token counts are estimated using a `words * 1.3` heuristic
- **Token Limits**: Set maximum token limits (default: 4,096)
- **Smart Truncation**: Context is truncated to fit within token limits if needed

### File Type Detection

Automatically detects programming language from file extension:

| Extension | Language |
|-----------|----------|
| `.py` | Python |
| `.js`, `.ts` | JavaScript/TypeScript |
| `.java` | Java |
| `.cpp`, `.c` | C/C++ |
| `.md` | Markdown |
| `.txt` | Plain text |
| And 30+ more... |

### Context Organization

Context items are formatted clearly:
```
## filename.py (D:\path\to\file.py)

```python
# File contents here...
```

================================================================================

USER REQUEST:
Your actual prompt goes here
```

## Context Templates

Pre-built templates are available in `D:\models\context-templates\`:

### 1. Code Analysis (`code_analysis.yaml`)
```yaml
name: "Code Analysis Context"
description: "Template for analyzing code files"
```

**Use for**: Code reviews, bug detection, refactoring suggestions

### 2. Documentation Writer (`documentation_writer.yaml`)
```yaml
name: "Documentation Writer Context"
description: "Template for writing comprehensive documentation"
```

**Use for**: Generating README files, API docs, usage guides

### 3. Debugging Assistant (`debugging_assistant.yaml`)
```yaml
name: "Debugging Assistant Context"
description: "Template for debugging code and troubleshooting issues"
```

**Use for**: Finding bugs, understanding error messages, fixing issues

## Context Menu Options

### [1] Add file(s) to context
- Add one or more files to the context
- Supports absolute or relative paths
- Automatically detects file language
- Shows token count for each file

### [2] Add text to context
- Add arbitrary text snippets
- Useful for error messages, logs, requirements
- Requires a label for organization

### [3] Remove context item
- Remove specific files or text from context
- Select by number from the list

### [4] Clear all context
- Remove all loaded context items
- Start fresh with a new context

### [5] Set token limit
- Adjust the maximum token limit
- Default: 4,096 tokens
- Recommended limits:
  - 4,096 - Small context (1-2 files)
  - 8,192 - Medium context (3-5 files)
  - 16,384 - Large context (6-10 files)
  - 32,768 - Extra large (10+ files)

### [6] Execute with context
- Run a model with all loaded context
- Auto-selects best model for your prompt
- Shows prompt preview before execution

## Usage Examples

### Example 1: Code Review

```python
# Step 1: Load files
Add file: main.py
Add file: utils.py
Add file: config.py

# Step 2: Execute
Prompt: "Review these files for potential bugs and security issues"

# Result: Model analyzes all 3 files together
```

### Example 2: Documentation Generation

```python
# Step 1: Load source code
Add file: api_router.py
Add file: database.py

# Step 2: Execute
Prompt: "Generate comprehensive API documentation with usage examples"

# Result: Model creates docs based on actual code
```

### Example 3: Debugging

```python
# Step 1: Load problematic code
Add file: buggy_script.py

# Step 2: Add error message as text
Add text:
Label: Error Message
Content:
```
Traceback (most recent call last):
  File "buggy_script.py", line 42, in process_data
    result = data['key']
KeyError: 'key'
```

# Step 3: Execute
Prompt: "Help me debug this error. Explain why it happens and how to fix it."
```

### Example 4: Multi-file Refactoring

```python
# Step 1: Load related files
Add file: models/user.py
Add file: models/product.py
Add file: services/auth.py

# Step 2: Execute
Prompt: "Suggest how to refactor these files to follow SOLID principles"
```

## Integration with Auto-Select Mode

The context system integrates with the auto-select model feature:

1. **Load context** (files/text)
2. **Execute with context**
3. **System detects use case** from your prompt
4. **Auto-recommends best model** (coding, reasoning, etc.)
5. **Runs model** with full context

## Token Estimation

Token counts are estimated using the formula:
```
tokens ≈ word_count × 1.3
```

This is a conservative estimate that works well for:
- Code (slightly over-estimates)
- Plain text (accurate)
- Technical documentation (slightly under-estimates)

### Token Guidelines

| Context Size | Files | Estimated Tokens | Recommended Limit |
|--------------|-------|------------------|-------------------|
| Small | 1-2 | 1,000-2,000 | 4,096 |
| Medium | 3-5 | 2,000-5,000 | 8,192 |
| Large | 6-10 | 5,000-10,000 | 16,384 |
| Extra Large | 10+ | 10,000-25,000 | 32,768 |

## Best Practices

### 1. Start Small
- Begin with 1-2 files
- Add more as needed
- Monitor token usage

### 2. Use Clear Labels
- Give descriptive labels to text items
- Labels help you track what's loaded
- Labels appear in the formatted prompt

### 3. Set Appropriate Token Limits
- Match limit to model context window
- Most models: 4,096-32,768 tokens
- Large models: up to 256K tokens

### 4. Review Before Execution
- Check the prompt preview (first 500 chars)
- Verify all needed context is loaded
- Ensure token limit isn't exceeded

### 5. Clear Context Between Sessions
- Use [4] Clear all context when switching tasks
- Prevents mixing unrelated context
- Reduces token usage

## Troubleshooting

### Problem: File Not Found
**Solution**: Use absolute paths or ensure relative paths are from the models directory

### Problem: Too Many Tokens
**Solutions**:
1. Increase token limit with [5]
2. Remove unnecessary files with [3]
3. Split into multiple smaller prompts

### Problem: Context Not Appearing in Response
**Solution**: Check prompt preview - ensure context was actually loaded

### Problem: Wrong Language Detected
**Solution**: The label doesn't affect detection - it's based on file extension only

## Technical Details

### ContextManager Class

Located in: `D:\models\context_manager.py`

**Key Methods**:
- `add_file(path, label)` - Add file to context
- `add_text(text, label)` - Add text to context
- `build_context_prompt(prompt)` - Build final prompt with context
- `estimate_tokens(text)` - Estimate token count
- `clear_context()` - Clear all context
- `get_context_summary()` - Get summary string

### Integration Points

The context system integrates with AIRouter in:
1. **Main menu** - Option [3]
2. **Auto-select mode** - Can use context
3. **Manual model selection** - Can use context

## Future Enhancements

Planned features:
- [ ] Load entire directories
- [ ] Git diff integration
- [ ] Context templates with variables
- [ ] Save/load context presets
- [ ] Folder watching for auto-reload
- [ ] Context compression for large files
- [ ] Syntax highlighting in preview
- [ ] Export context to file

## API Reference

See `context_manager.py` for full API documentation.

## See Also

- [HOW-TO-RUN-AI-ROUTER.md](HOW-TO-RUN-AI-ROUTER.md) - Main usage guide
- [SYSTEM-PROMPTS-QUICK-START.md](SYSTEM-PROMPTS-QUICK-START.md) - System prompts
- [2025-RESEARCH-SUMMARY.md](2025-RESEARCH-SUMMARY.md) - Model optimization guide
