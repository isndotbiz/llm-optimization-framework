# Model Comparison Mode (A/B Testing) - Integration Guide

## Overview

This guide walks you through integrating the Model Comparison Mode into the AI Router application. This feature allows side-by-side testing of 2-4 models with the same prompt to compare performance, quality, and speed.

## Files Created

### 1. `model_comparison.py` (D:\models\model_comparison.py)
**Status:** ✅ Complete

Contains:
- `ComparisonResult` dataclass - Stores comparison session data
- `ModelComparison` class - Manages comparisons, display, and export
- Methods for creating, displaying, and exporting comparisons
- Database integration methods

**Key Features:**
- Create comparisons from multiple model responses
- Display side-by-side results with syntax highlighting
- Display performance metrics table
- Export to JSON or Markdown
- Save/load from database

### 2. `comparison_schema.sql` (D:\models\comparison_schema.sql)
**Status:** ✅ Complete

Database schema for storing comparisons:
- `comparison_results` table - Main comparison metadata
- `comparison_responses` table - Individual model responses
- Indexes for performance
- `recent_comparisons` view for easy querying

**Note:** This schema is optional. The current implementation can store comparisons in the existing `session_metadata` table or as JSON/Markdown exports.

### 3. `comparison_integration.py` (D:\models\comparison_integration.py)
**Status:** ✅ Complete

Contains all code needed for integration:
- Import statements
- Initialization code
- Helper methods (`select_multiple_models()`, `comparison_mode()`)
- Menu updates
- Usage instructions

## Integration Steps

### Step 1: Add Import Statement

**File:** `ai-router.py`
**Location:** Line ~24 (after other imports)

Add:
```python
from model_comparison import ModelComparison, ComparisonResult
```

### Step 2: Initialize Model Comparison

**File:** `ai-router.py`
**Location:** In `AIRouter.__init__()`, after line 413 (after `self.session_manager` initialization)

Add:
```python
# Initialize model comparison
comparisons_dir = self.models_dir / "comparisons"
self.model_comparison = ModelComparison(comparisons_dir)
```

### Step 3: Add Helper Methods

**File:** `ai-router.py`
**Location:** In `AIRouter` class (can add after `cleanup_sessions()` method around line 1173)

Add these two methods from `comparison_integration.py`:

1. `select_multiple_models()` - Interactive multi-model selection
2. `comparison_mode()` - Main comparison mode interface

**Copy the complete method implementations from `comparison_integration.py`.**

### Step 4: Update Interactive Menu Display

**File:** `ai-router.py`
**Location:** In `interactive_mode()`, around line 589

**Current:**
```python
print(f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET} 📚 View documentation guides")

# Bypass mode toggle option
bypass_status = f"{Colors.BRIGHT_GREEN}ON{Colors.RESET}" if self.bypass_mode else f"{Colors.BRIGHT_RED}OFF{Colors.RESET}"
print(f"{Colors.BRIGHT_GREEN}[8]{Colors.RESET} 🔓 Toggle Auto-Yes Mode (Currently: {bypass_status})")

print(f"{Colors.BRIGHT_GREEN}[9]{Colors.RESET} 🚪 Exit")
```

**Updated:**
```python
print(f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET} 📚 View documentation guides")
print(f"{Colors.BRIGHT_GREEN}[8]{Colors.RESET} 🔄 Model Comparison Mode (A/B Testing)")

# Bypass mode toggle option
bypass_status = f"{Colors.BRIGHT_GREEN}ON{Colors.RESET}" if self.bypass_mode else f"{Colors.BRIGHT_RED}OFF{Colors.RESET}"
print(f"{Colors.BRIGHT_GREEN}[9]{Colors.RESET} 🔓 Toggle Auto-Yes Mode (Currently: {bypass_status})")

print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} 🚪 Exit")
```

### Step 5: Update Menu Choice Handler

**File:** `ai-router.py`
**Location:** In `interactive_mode()`, around line 600-620

**Current:**
```python
elif choice == "7":
    self.view_documentation()
elif choice == "8":
    self.toggle_bypass_mode()
elif choice == "9":
    print(f"\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\n")
    sys.exit(0)
```

**Updated:**
```python
elif choice == "7":
    self.view_documentation()
elif choice == "8":
    self.comparison_mode()
elif choice == "9":
    self.toggle_bypass_mode()
elif choice == "0":
    print(f"\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\n")
    sys.exit(0)
```

## Testing the Integration

### 1. Basic Test
```bash
python ai-router.py
# Select option [8] Model Comparison Mode
# Enter a test prompt
# Select 2 models (e.g., 1,2)
# Wait for results
# Review side-by-side comparison
```

### 2. Export Test
After running a comparison:
- Select [1] to export as JSON
- Select [2] to export as Markdown
- Check `D:\models\comparisons\` for exported files

### 3. Database Test
After running a comparison:
- Select [3] to save to database
- Verify no errors occur

## Example Comparison Output

### Side-by-Side Display
```
╔══════════════════════════════════════════════════════════════╗
║  MODEL COMPARISON RESULTS
╚══════════════════════════════════════════════════════════════╝

Prompt:
Write a Python function to calculate fibonacci numbers

────────────────────────────────────────────────────────────────

[1] Qwen3 Coder 30B Q4_K_M
Model ID: qwen3-coder-30b

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
...

────────────────────────────────────────────────────────────────

[2] Phi-4 Reasoning Plus 14B Q6_K
Model ID: phi4-14b

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
...
```

### Performance Metrics Table
```
╔══════════════════════════════════════════════════════════════╗
║  PERFORMANCE METRICS
╚══════════════════════════════════════════════════════════════╝

Model                          In/Out Tokens        Duration     Tok/Sec
────────────────────────────────────────────────────────────────
Qwen3 Coder 30B Q4_K_M        45/120              4.50s        26.7 tok/s
Phi-4 Reasoning Plus 14B      45/85               2.10s        40.5 tok/s ⭐

⭐ Fastest: Phi-4 Reasoning Plus 14B (40.5 tok/s)
```

## Exported File Formats

### JSON Export (comparison_YYYYMMDD_HHMMSS.json)
```json
{
  "comparison_id": "uuid-here",
  "timestamp": "2025-12-08T10:30:00",
  "prompt": "Write a Python function...",
  "responses": [
    {
      "model_id": "qwen3-coder-30b",
      "model_name": "Qwen3 Coder 30B Q4_K_M",
      "response": "def fibonacci...",
      "tokens_input": 45,
      "tokens_output": 120,
      "duration": 4.5
    }
  ],
  "winner": null,
  "notes": null
}
```

### Markdown Export (comparison_YYYYMMDD_HHMMSS.md)
Complete report with:
- Comparison metadata
- Performance metrics table
- Full responses for each model
- Optional notes and winner designation

## Database Storage

### Using Session Metadata Table (Current Implementation)
Comparisons are stored as metadata entries:
- Key: `comparison_<field_name>`
- Values: JSON-encoded data
- Responses stored as `comparison_response_0`, `comparison_response_1`, etc.

### Using Dedicated Tables (Optional)
If you want dedicated comparison tables:
1. Execute `comparison_schema.sql` on the session database
2. Update `save_comparison_to_db()` to use the new tables

```bash
sqlite3 D:\models\.ai-router-sessions.db < D:\models\comparison_schema.sql
```

## Troubleshooting

### Import Error
**Error:** `ModuleNotFoundError: No module named 'model_comparison'`

**Solution:** Ensure `model_comparison.py` is in the same directory as `ai-router.py` (D:\models\)

### Directory Creation Error
**Error:** Permission denied when creating comparisons directory

**Solution:** Manually create the directory:
```bash
mkdir D:\models\comparisons
```

### Model Execution Fails
**Error:** One or more models fail during comparison

**Solution:**
- Ensure models are properly configured
- Check model paths in `ModelDatabase`
- Run models individually first to verify they work

### Colors Not Displaying
**Issue:** Comparison display shows ANSI codes instead of colors

**Solution:** Ensure terminal supports ANSI color codes. Works in:
- Git Bash
- WSL terminal
- Windows Terminal
- Most modern terminals

## Advanced Usage

### Custom Comparison Analysis
You can extend `ComparisonResult` to add:
- Quality scoring
- Automatic winner selection based on criteria
- Response similarity analysis
- Cost/performance optimization metrics

### Batch Comparisons
Combine with `BatchProcessor` to run comparisons across multiple prompts:
```python
prompts = ["prompt1", "prompt2", "prompt3"]
for prompt in prompts:
    # Run comparison_mode() programmatically
```

### Integration with Session History
Link comparisons to sessions for tracking:
```python
# Store comparison_id in session metadata
session_manager.set_session_metadata(session_id, "comparison_id", comparison.comparison_id)
```

## Summary

All files are ready at:
- ✅ `D:\models\model_comparison.py` - Main implementation
- ✅ `D:\models\comparison_schema.sql` - Database schema (optional)
- ✅ `D:\models\comparison_integration.py` - Integration code & instructions

**Next Steps:**
1. Follow Steps 1-5 above to integrate into `ai-router.py`
2. Test with option [8] in the main menu
3. Export comparisons to review formats
4. Optionally set up dedicated database tables

**Integration Time:** ~10 minutes for manual code insertion

The system is fully implemented and ready to use!
