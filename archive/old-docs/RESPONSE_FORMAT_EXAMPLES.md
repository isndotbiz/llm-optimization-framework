# Response Post-Processing Format Examples

## 1. Standard Text Response Format

**File**: `response_20251208_153000.txt`

```
================================================================================
AI ROUTER - MODEL RESPONSE
================================================================================
Generated: 2025-12-08 15:30:00
Model: Qwen3 Coder 30B Q4_K_M
================================================================================

This is the actual response content from the model.
It preserves all formatting, line breaks, and content exactly as generated.
```

## 2. Markdown Export Format

**File**: `response_20251208_153000.md`

```markdown
# AI Router Response

**Generated:** 2025-12-08 15:30:00
**Model:** Qwen3 Coder 30B Q4_K_M

---

## Response

This is the actual response content from the model.
Formatted as clean markdown for easy reading and sharing.
```

## 3. Extracted Code Block Format

**File**: `factorial_code_0.py`

```python
# Language: python

def factorial(n):
    """Calculate factorial of n"""
    if n < 0:
        raise ValueError("Negative numbers not allowed")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
```

## 4. Response with Multiple Code Blocks

**Original Response**:
```
Here's a Python function and a test script:

```python
def add(a, b):
    return a + b
```

And here's how to test it:

```bash
python test_add.py
```
```

**Extracted Files**:

`mycode_code_0.py`:
```python
# Language: python

def add(a, b):
    return a + b
```

`mycode_code_1.sh`:
```bash
# Language: bash

python test_add.py
```

## 5. Statistics Output Example

```
Response Statistics

Characters:     1,245
Words:          312
Lines:          45
Code blocks:    2
Avg line length: 27.7 chars
```

## 6. List Saved Responses Example

```
Recently Saved Responses

Last 3 response(s):

[1] response_20251208_153045.txt
     2025-12-08 15:30:45

[2] response_20251208_152030.txt
     2025-12-08 15:20:30

[3] response_20251208_151500.txt
     2025-12-08 15:15:00
```

## 7. Post-Processing Menu Example

```
╔══════════════════════════════════════════════════════════════╗
║  RESPONSE POST-PROCESSING
╚══════════════════════════════════════════════════════════════╝

Model: Qwen3 Coder 30B Q4_K_M

[1] Save to file
[2] Extract code blocks
[3] Show statistics
[4] Copy to clipboard
[5] Export as markdown
[6] List saved responses
[0] Continue

Select option [0-6]:
```

## 8. Interactive Flow Example

### User generates a response:
```
✓ Model execution complete!

Post-process this response? [y/N]: y
```

### User enters post-processing menu:
```
[Opens menu with options 1-6]

Select option [0-6]: 1
```

### User saves to file:
```
Save Response to File

Press Enter for auto-generated filename, or type a custom name:
Filename: my_factorial_solution

✓ Response saved to:
D:\models\outputs\my_factorial_solution.txt
```

### User extracts code blocks:
```
Select option [0-6]: 2

Extract Code Blocks

Found 2 code block(s):

[1] Language: python
    Lines: 15

[2] Language: python
    Lines: 8

Save all code blocks to files? [Y/n]: y
Base filename (default: 'code'): factorial

✓ Saved 2 code file(s):

  factorial_code_0.py
  factorial_code_1.py
```

### User views statistics:
```
Select option [0-6]: 3

Response Statistics

Characters:     1,567
Words:          298
Lines:          52
Code blocks:    2
Avg line length: 30.1 chars
```

### User copies to clipboard (with pyperclip):
```
Select option [0-6]: 4

Copy to Clipboard

✓ Response copied to clipboard!
```

### User copies to clipboard (without pyperclip):
```
Select option [0-6]: 4

Copy to Clipboard

⚠ Clipboard functionality not available.
Install pyperclip: pip install pyperclip
```

## File Extension Mapping Reference

| Language | Extension | Example File |
|----------|-----------|--------------|
| python | .py | `code_0.py` |
| javascript | .js | `code_0.js` |
| typescript | .ts | `code_0.ts` |
| java | .java | `code_0.java` |
| cpp, c++ | .cpp | `code_0.cpp` |
| c | .c | `code_0.c` |
| rust | .rs | `code_0.rs` |
| go | .go | `code_0.go` |
| bash, shell | .sh | `code_0.sh` |
| sql | .sql | `code_0.sql` |
| html | .html | `code_0.html` |
| css | .css | `code_0.css` |
| json | .json | `code_0.json` |
| yaml, yml | .yaml | `code_0.yaml` |
| markdown, md | .md | `code_0.md` |
| (other) | .txt | `code_0.txt` |

## Metadata Header Customization

The metadata header can include additional fields by passing a `metadata` dict:

```python
metadata = {
    "Prompt": "Calculate factorial",
    "Temperature": 0.7,
    "Tokens": "512"
}

filepath = response_processor.save_response(
    response_text,
    model_name="Qwen3 Coder 30B",
    metadata=metadata
)
```

**Result**:
```
================================================================================
AI ROUTER - MODEL RESPONSE
================================================================================
Generated: 2025-12-08 15:30:00
Model: Qwen3 Coder 30B
Prompt: Calculate factorial
Temperature: 0.7
Tokens: 512
================================================================================

[Response...]
```

## Directory Structure After Usage

```
D:\models\outputs\
├── response_20251208_143000.txt       # Auto-generated filename
├── response_20251208_150000.txt       # Another auto-generated
├── my_factorial_solution.txt          # Custom filename
├── python_tutorial.md                 # Markdown export
├── factorial_code_0.py                # Extracted code block
├── factorial_code_1.py                # Another code block
├── api_example_code_0.js              # JavaScript code
└── api_example_code_1.sh              # Shell script
```

## Best Practices

1. **Use descriptive base names** when extracting code blocks
   - Good: `factorial`, `api_client`, `test_suite`
   - Avoid: `code`, `temp`, `x`

2. **Custom filenames for important responses**
   - Save tutorials, examples, solutions with meaningful names
   - Use auto-generated names for quick tests

3. **Export as markdown** for sharing
   - Markdown is more readable for documentation
   - Includes metadata in clean format
   - Easy to paste into issues, wikis, etc.

4. **Extract code blocks immediately**
   - Easier to test and run code in separate files
   - Preserves syntax highlighting
   - Can be imported into projects

5. **Check statistics** to understand response size
   - Helps gauge model verbosity
   - Useful for token count estimation
   - Track code-to-text ratio
