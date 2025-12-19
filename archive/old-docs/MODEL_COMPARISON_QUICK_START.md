# Model Comparison Mode - Quick Start Guide

## What is Model Comparison Mode?

A/B testing feature that allows you to test the same prompt with 2-4 models simultaneously and compare:
- **Response Quality** - Side-by-side text comparison
- **Performance** - Speed (tokens/sec), duration
- **Token Usage** - Input/output token counts
- **Overall Winner** - Which model performed best

## How to Use

### Step 1: Launch Comparison Mode
```bash
python ai-router.py
# Select [8] Model Comparison Mode (A/B Testing)
```

### Step 2: Enter Your Prompt
```
Enter prompt to test: Write a function to calculate fibonacci numbers
```

### Step 3: Select 2-4 Models
```
Select 2-4 models for comparison
Enter numbers separated by commas (e.g., 1,3,5)

Your selection: 1,2,5
```

### Step 4: Wait for Results
The system will run each model sequentially:
```
[1/3] Testing Qwen3 Coder 30B Q4_K_M...
✓ Complete (4.50s)

[2/3] Testing Phi-4 Reasoning Plus 14B Q6_K...
✓ Complete (2.10s)

[3/3] Testing Dolphin 3.0 Llama 3.1 8B Q6_K...
✓ Complete (0.90s)
```

### Step 5: Review Comparison

#### Side-by-Side Results
See each model's complete response with:
- Model name and ID
- Full response text
- Organized display

#### Performance Metrics Table
```
Model                          In/Out Tokens    Duration    Tok/Sec
─────────────────────────────────────────────────────────────────
Qwen3 Coder 30B Q4_K_M        45/120          4.50s       26.7 tok/s
Phi-4 Reasoning Plus 14B      45/85           2.10s       40.5 tok/s
Dolphin 3.0 Llama 3.1 8B      45/40           0.90s       44.4 tok/s ⭐

⭐ Fastest: Dolphin 3.0 Llama 3.1 8B (44.4 tok/s)
```

### Step 6: Export or Save (Optional)

Post-comparison menu:
```
[1] Export comparison (JSON)     - Machine-readable format
[2] Export comparison (Markdown) - Human-readable report
[3] Save to database            - Store for later analysis
[4] Run another comparison      - Start new test
[0] Back to main menu           - Return to main menu
```

## When to Use Comparison Mode

### ✅ Best For:
- **Evaluating new models** - Test before committing to a model
- **Optimizing for speed** - Find fastest model for a task type
- **Quality assessment** - Compare response accuracy and detail
- **Model selection** - Choose best model for specific use cases
- **Benchmarking** - Create performance baselines
- **Documentation** - Generate comparison reports for teams

### ❌ Not Ideal For:
- **Single-model tasks** - Use regular auto-select mode
- **Long conversations** - Comparison is for single prompts only
- **Quick queries** - Overhead of running 2-4 models
- **Cost-sensitive scenarios** - Uses multiple models (more resources)

## Example Use Cases

### 1. Code Generation Test
```
Prompt: "Write a Python function to merge two sorted lists"
Models: qwen3-coder-30b, qwen25-coder-32b, phi4-14b
Goal: Find which produces most efficient code
```

### 2. Reasoning Comparison
```
Prompt: "Explain quantum entanglement in simple terms"
Models: phi4-14b, ministral-3-14b, deepseek-r1-14b
Goal: Compare explanation quality
```

### 3. Speed Benchmark
```
Prompt: "What is the capital of France?"
Models: dolphin-llama31-8b, phi4-14b, qwen3-coder-30b
Goal: Identify fastest model for simple queries
```

### 4. Creative Writing
```
Prompt: "Write a short poem about technology"
Models: gemma3-27b, dolphin-mistral-24b, llama33-70b
Goal: Compare creative quality
```

## Export Formats

### JSON Export (comparison_YYYYMMDD_HHMMSS.json)
- **Use Case:** Data analysis, scripting, automation
- **Contains:** Complete structured data
- **Location:** `D:\models\comparisons\`

**Example:**
```json
{
  "comparison_id": "uuid",
  "timestamp": "2025-12-08T14:30:45",
  "prompt": "...",
  "responses": [...],
  "winner": "model-id",
  "notes": "..."
}
```

### Markdown Export (comparison_YYYYMMDD_HHMMSS.md)
- **Use Case:** Documentation, sharing, reports
- **Contains:** Formatted report with tables
- **Location:** `D:\models\comparisons\`

**Includes:**
- Comparison metadata
- Performance metrics table
- Full responses with syntax highlighting
- Notes and winner designation

### Database Storage
- **Use Case:** Long-term tracking, analytics
- **Storage:** SQLite session database
- **Query:** Use session metadata or dedicated tables

## Tips & Best Practices

### 1. Choose Appropriate Models
- **Similar size** - More fair comparison
- **Different strengths** - Test varied capabilities
- **Use case match** - Select models suited to task type

### 2. Write Clear Prompts
- **Specific** - "Write a bubble sort in Python" vs "Write code"
- **Measurable** - Makes comparison easier
- **Consistent** - Same prompt across all models

### 3. Interpret Results Wisely
- **Speed isn't everything** - Faster ≠ better quality
- **Context matters** - Different tasks need different models
- **Look at all metrics** - Tokens, duration, quality

### 4. Document Findings
- **Export comparisons** - Save for future reference
- **Add notes** - Record your observations
- **Track patterns** - Which models excel at what?

## Keyboard Shortcuts & Navigation

```
Main Menu -> [8] -> Comparison Mode
Enter prompt -> Select models (1,3,5) -> Wait -> Review

Post-comparison:
[1] JSON export
[2] Markdown export
[3] Database save
[4] New comparison
[0] Main menu
```

## Quick Troubleshooting

### Models fail during comparison
- **Solution:** Run models individually first to test
- **Check:** Model paths in configuration
- **Verify:** Sufficient VRAM/RAM available

### Performance seems slow
- **Expected:** Running multiple large models takes time
- **Tip:** Start with 2 models, then expand
- **Consider:** Use smaller/faster models for testing

### Can't find exported files
- **Location:** `D:\models\comparisons\`
- **Create manually:** `mkdir D:\models\comparisons`
- **Check permissions:** Ensure write access

### Colors not showing
- **Terminal:** Use Git Bash, WSL, or Windows Terminal
- **Fallback:** Results still readable without colors

## Advanced Features

### Programmatic Comparison
You can call comparison methods directly:
```python
router = AIRouter()
result = router.model_comparison.create_comparison(prompt, responses)
router.model_comparison.display_comparison(result, colors=Colors)
```

### Custom Analysis
Extend `ComparisonResult` class to add:
- Quality scoring algorithms
- Cost analysis
- Response similarity metrics
- Automatic winner selection

### Batch Comparisons
Run same models across multiple prompts:
```python
prompts = ["prompt1", "prompt2", "prompt3"]
models = ["model1", "model2"]
# Run comparison for each prompt
```

## Summary

**Model Comparison Mode** lets you:
- ✅ Test 2-4 models with same prompt
- ✅ Compare side-by-side results
- ✅ Review performance metrics
- ✅ Export to JSON or Markdown
- ✅ Save to database for tracking

**Perfect for:** Model evaluation, benchmarking, optimization, documentation

**Access via:** Main menu option [8]

**Output location:** `D:\models\comparisons\`

---

For detailed integration instructions, see: `MODEL_COMPARISON_INTEGRATION_GUIDE.md`
