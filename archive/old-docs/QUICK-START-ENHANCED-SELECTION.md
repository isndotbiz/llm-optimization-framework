# Quick Start: Enhanced Smart Model Selection

## What's New?

The AI Router now features an **intelligent model selection system** with:
- **Confidence Scoring** - Know how confident the system is about its choice
- **Top 3 Recommendations** - See alternative models for your task
- **Preference Learning** - System remembers your model preferences
- **Visual Feedback** - Easy-to-read confidence bars and explanations

---

## How to Use

### 1. Start AI Router
```bash
python ai-router.py
```

### 2. Select Auto-Select Mode
```
[1] Auto-select model based on prompt
```

### 3. Enter Your Prompt
```
> Write a Python function to sort a list
```

### 4. Review Smart Selection
The system will show:
- **Detected Category** (coding, math, creative, research, etc.)
- **Confidence Score** with visual bar
- **Explanation** of why this model was selected
- **Top 3 Recommendations** with confidence scores
- **Detailed Model Info**

### 5. Save Preference (Optional)
If confidence is high (≥60%), you'll be asked:
```
Save this model as preferred for [category] tasks? [y/N]:
```

Answer `y` to remember this choice for future tasks.

### 6. Run or Cancel
```
Run this model? [Y/n]:
```

---

## Example Output

```
╔══════════════════════════════════════════════════════════════╗
║  SMART MODEL SELECTION RESULTS
╚══════════════════════════════════════════════════════════════╝

Detected Category: CODING
Confidence Score: ██████████ 100%

Why this selection?
Selected coding model with high confidence (100%) - detected code-related
keywords like 'function', 'debug', 'implement'

Selected Model: Qwen3 Coder 30B Q4_K_M

Model Recommendations (Top 3):
────────────────────────────────────────────────────────────
1. Qwen3 Coder 30B Q4_K_M
   Category: coding
   Confidence: ██████████ 100%
   Advanced coding, code review, architecture design

2. Qwen2.5 Coder 32B Q4_K_M
   Category: coding
   Confidence: ██████████ 100%
   Coding, debugging, technical documentation
────────────────────────────────────────────────────────────
```

---

## Categories Detected

The system can detect these task categories:

| Category | Example Prompts |
|----------|----------------|
| **Coding** | "Write a Python function", "Debug this code", "Implement algorithm" |
| **Math** | "Solve equation", "Calculate probability", "Prove theorem" |
| **Reasoning** | "Analyze this problem", "Logic puzzle", "Deduce the answer" |
| **Creative** | "Write a story", "Create a poem", "Imagine a scenario" |
| **Research** | "Explain quantum computing", "Compare X and Y", "Summarize this topic" |
| **General** | Anything that doesn't fit above categories |

---

## Confidence Levels

| Score | Visual | Meaning |
|-------|--------|---------|
| **≥70%** | ██████████ | High - Strong keyword matches, clear category |
| **40-69%** | █████░░░░░ | Medium - Moderate keyword matches |
| **<40%** | ██░░░░░░░░ | Low - Weak matches, using general model |

---

## Preference Learning

### How It Works
1. System detects task category with high confidence (≥60%)
2. Asks if you want to save this model for that category
3. Saves your choice to `D:\models\.ai-router-preferences.json`
4. Next time same category detected, uses your preferred model

### Example Preference File
```json
{
  "coding": "qwen25-coder-32b",
  "math": "phi4-14b",
  "creative": "gemma3-27b",
  "research": "llama33-70b"
}
```

### Reset Preferences
Delete or edit: `D:\models\.ai-router-preferences.json`

---

## Tips for Best Results

1. **Be Specific** - "Write Python sorting function" > "Help with code"
2. **Use Keywords** - Include words like "code", "math", "creative", "research"
3. **Save Preferences** - Let the system learn your favorite models
4. **Check Recommendations** - Review all 3 suggestions before running
5. **Trust Low Confidence** - If confidence is low, consider being more specific

---

## Test the System

Run the test script to see all features:
```bash
python test_enhanced_selection.py
```

This will demonstrate:
- Confidence scoring for different prompts
- Category detection
- Model recommendations
- Preference learning

---

## Files Reference

| File | Purpose |
|------|---------|
| `model_selector.py` | Core selection engine |
| `ai-router.py` | Main application (enhanced) |
| `.ai-router-preferences.json` | Your saved preferences |
| `test_enhanced_selection.py` | Test/demo script |
| `ENHANCED-SELECTION-EXAMPLE-OUTPUT.md` | Detailed examples |
| `ENHANCEMENT-SUMMARY.md` | Technical details |

---

## Troubleshooting

### "No preference file found"
Normal on first run. Preferences will be created when you save your first choice.

### "Low confidence score for everything"
Try being more specific with keywords. The system learns from clear task descriptions.

### "Wrong category detected"
Review the top 3 recommendations - you might want a different model from the list.

### "Preferences not saving"
Check write permissions for `D:\models\.ai-router-preferences.json`

---

## What's Next?

The enhanced selection system will continue to improve as you use it:
- Saved preferences become more refined
- Pattern matching adapts to your usage
- Recommendations become more personalized

**Enjoy smarter model selection!**
