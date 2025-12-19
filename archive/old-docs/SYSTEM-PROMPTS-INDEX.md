# System Prompts Index - RTX 3090 Models
## Complete File Listing & Navigation Guide

**Created:** December 8, 2024
**Total Files:** 10 prompt files + 3 documentation files

---

## Prompt Files (10 Total)

### System Prompt Files (8 Models)

#### 1. Qwen3 Coder 30B
- **File:** `D:\models\organized\system-prompt-qwen3-coder-30b.txt`
- **Size:** 1.7KB
- **Model ID:** `qwen3-coder-30b`
- **Use:** SWE-bench champion, agentic workflows, 256K context

#### 2. Qwen2.5 Coder 32B
- **File:** `D:\models\organized\system-prompt-qwen25-coder-32b.txt`
- **Size:** 1.6KB
- **Model ID:** `qwen25-coder-32b`
- **Use:** Multi-language code generation, #1 code repair

#### 3. Phi-4 Reasoning Plus 14B
- **File:** `D:\models\organized\system-prompt-phi4-14b.txt`
- **Size:** 2.0KB
- **Model ID:** `phi4-14b`
- **Use:** STEM, math reasoning, 78% AIME

#### 4. Ministral-3 14B Reasoning
- **File:** `D:\models\organized\system-prompt-ministral-3-14b.txt`
- **Size:** 1.4KB
- **Model ID:** `ministral-3-14b`
- **Use:** AIME champion (85%), 256K context

#### 5. DeepSeek R1 14B
- **File:** `D:\models\organized\system-prompt-deepseek-r1.txt`
- **Size:** 2.2KB
- **Model ID:** `deepseek-r1-14b`
- **Use:** Chain-of-thought reasoning (USER PROMPTS ONLY!)

#### 6. Llama 3.3 70B Abliterated
- **File:** `D:\models\organized\system-prompt-llama33-70b.txt`
- **Size:** 1.6KB
- **Model ID:** `llama33-70b`
- **Use:** Largest model, deep reasoning, 128K context

#### 7. Dolphin 3.0 Llama 3.1 8B
- **File:** `D:\models\organized\system-prompt-dolphin-8b.txt`
- **Size:** 917 bytes
- **Model ID:** `dolphin-llama31-8b`
- **Use:** Speed champion (60-90 tok/sec)

#### 8. Wizard Vicuna 13B Uncensored
- **File:** `D:\models\organized\system-prompt-wizard-vicuna.txt`
- **Size:** 782 bytes
- **Model ID:** `wizard-vicuna-13b`
- **Use:** Classic uncensored, general chat

---

### User Prompt Templates (2 Models - NO System Prompt Support)

#### 9. Gemma-3 27B Abliterated
- **File:** `D:\models\organized\user-prompt-template-gemma3-27b.txt`
- **Size:** 4.8KB
- **Model ID:** `gemma3-27b`
- **Use:** Creative writing, 128K context, CO-STAR framework
- **Note:** NO system prompt support - embed instructions in user message

#### 10. Dolphin Mistral 24B Venice Edition
- **File:** `D:\models\organized\user-prompt-template-dolphin-mistral-24b.txt`
- **Size:** 5.4KB
- **Model ID:** `dolphin-mistral-24b`
- **Use:** Uncensored chat, 2.2% refusal rate
- **Note:** NO system prompt support - embed instructions in user message

---

## Documentation Files (3 Total)

### 1. Comprehensive Summary
- **File:** `D:\models\SYSTEM-PROMPTS-SUMMARY.md`
- **Size:** 14KB
- **Content:** Complete guide with benchmarks, use cases, parameters, warnings
- **Audience:** Detailed reference for all models

### 2. Quick Reference Card
- **File:** `D:\models\SYSTEM-PROMPTS-QUICK-REFERENCE.md`
- **Size:** ~10KB
- **Content:** At-a-glance guide, critical warnings, common patterns
- **Audience:** Quick lookups and decision-making

### 3. This Index
- **File:** `D:\models\SYSTEM-PROMPTS-INDEX.md`
- **Size:** ~3KB
- **Content:** File listing and navigation
- **Audience:** Finding files and understanding structure

---

## File Organization

```
D:\models\
├── organized\                                    # Model files and prompts
│   ├── system-prompt-qwen3-coder-30b.txt        # Qwen3 30B system prompt
│   ├── system-prompt-qwen25-coder-32b.txt       # Qwen2.5 32B system prompt
│   ├── system-prompt-phi4-14b.txt               # Phi-4 14B system prompt
│   ├── system-prompt-ministral-3-14b.txt        # Ministral-3 14B system prompt
│   ├── system-prompt-deepseek-r1.txt            # DeepSeek R1 user template
│   ├── system-prompt-llama33-70b.txt            # Llama 3.3 70B system prompt
│   ├── system-prompt-dolphin-8b.txt             # Dolphin 8B system prompt
│   ├── system-prompt-wizard-vicuna.txt          # Wizard Vicuna 13B system prompt
│   ├── user-prompt-template-gemma3-27b.txt      # Gemma-3 27B user template
│   ├── user-prompt-template-dolphin-mistral-24b.txt  # Dolphin 24B user template
│   └── [model GGUF files...]
│
├── SYSTEM-PROMPTS-SUMMARY.md                    # Comprehensive 14KB guide
├── SYSTEM-PROMPTS-QUICK-REFERENCE.md            # Quick reference card
├── SYSTEM-PROMPTS-INDEX.md                      # This file
├── MODEL_REFERENCE_GUIDE.md                     # Original research source
└── ai-router.py                                 # Automated model selector
```

---

## File Naming Convention

### System Prompts (Auto-loaded by AI Router)
```
Pattern: system-prompt-{model-id}.txt
Example: system-prompt-phi4-14b.txt

Model IDs match ai-router.py exactly:
- qwen3-coder-30b
- qwen25-coder-32b
- phi4-14b
- ministral-3-14b
- deepseek-r1-14b
- llama33-70b
- dolphin-llama31-8b
- wizard-vicuna-13b
```

### User Templates (For models without system prompt support)
```
Pattern: user-prompt-template-{model-id}.txt
Example: user-prompt-template-gemma3-27b.txt

Model IDs:
- gemma3-27b
- dolphin-mistral-24b
```

---

## Models by Category

### Coding Excellence
```
1. system-prompt-qwen3-coder-30b.txt         → SWE-bench champion
2. system-prompt-qwen25-coder-32b.txt        → Multi-lang, code repair
3. system-prompt-phi4-14b.txt                → Programming logic
```

### Mathematical Reasoning
```
1. system-prompt-ministral-3-14b.txt         → 85% AIME (best at 14B)
2. system-prompt-phi4-14b.txt                → 78% AIME, STEM
3. system-prompt-deepseek-r1.txt             → Chain-of-thought
```

### Creative Writing
```
1. user-prompt-template-gemma3-27b.txt       → 128K context, abliterated
2. user-prompt-template-dolphin-mistral-24b.txt → 2.2% refusal
3. system-prompt-wizard-vicuna.txt           → Classic uncensored
```

### Large-Scale Reasoning
```
1. system-prompt-llama33-70b.txt             → Largest (70B), 128K context
2. system-prompt-ministral-3-14b.txt         → 256K context
3. system-prompt-qwen3-coder-30b.txt         → 256K context
```

### Speed & Efficiency
```
1. system-prompt-dolphin-8b.txt              → 60-90 tok/sec
2. system-prompt-phi4-14b.txt                → 35-55 tok/sec
3. system-prompt-ministral-3-14b.txt         → 35-50 tok/sec
```

---

## Critical Files by Use Case

### If You Want...

**...to generate production code:**
→ `system-prompt-qwen3-coder-30b.txt` or `system-prompt-qwen25-coder-32b.txt`

**...to solve AIME-level math:**
→ `system-prompt-ministral-3-14b.txt` (85%) or `system-prompt-phi4-14b.txt` (78%)

**...to write creative content:**
→ `user-prompt-template-gemma3-27b.txt` (128K) or `user-prompt-template-dolphin-mistral-24b.txt`

**...deep research analysis:**
→ `system-prompt-llama33-70b.txt` (70B params) or `system-prompt-ministral-3-14b.txt` (256K context)

**...fast responses:**
→ `system-prompt-dolphin-8b.txt` (60-90 tok/sec speed champion)

**...unrestricted discussion:**
→ `system-prompt-llama33-70b.txt`, `user-prompt-template-gemma3-27b.txt`, or `user-prompt-template-dolphin-mistral-24b.txt`

---

## Special Considerations

### Models Requiring Special Handling

#### DeepSeek R1 14B
- **File:** `system-prompt-deepseek-r1.txt`
- **Critical:** Performs WORSE with system prompts!
- **Usage:** User prompts only, zero-shot, minimal instructions
- **Template:** "Please reason step by step, and put your final answer within \boxed{}."

#### Gemma-3 27B
- **File:** `user-prompt-template-gemma3-27b.txt`
- **Critical:** NO system prompt support
- **Usage:** Embed ALL instructions in user message using CO-STAR framework

#### Dolphin Mistral 24B
- **File:** `user-prompt-template-dolphin-mistral-24b.txt`
- **Critical:** NO system prompt support
- **Usage:** Embed instructions in user message OR use direct prompting

---

## Temperature Warnings

### NEVER Use Temperature 0
```
⚠️ system-prompt-qwen3-coder-30b.txt       → Causes infinite loops
⚠️ system-prompt-qwen25-coder-32b.txt      → Causes infinite loops

Always use temp ≥ 0.6 (recommended: 0.7) for Qwen models
```

### Do NOT Use "Think Step-by-Step"
```
⚠️ system-prompt-phi4-14b.txt              → Degrades reasoning performance

Reasoning already built into architecture. Present problems directly.
```

---

## Required Flags (Auto-configured in AI Router)

```
✓ system-prompt-phi4-14b.txt               → Requires --jinja flag
✓ system-prompt-qwen3-coder-30b.txt        → Requires --jinja flag

These are automatically added by ai-router.py when selecting these models.
```

---

## Integration with AI Router

All prompts are automatically loaded by `ai-router.py`:

1. User selects model (interactive or auto-detect)
2. Router checks `model_data['system_prompt']` field
3. Loads corresponding file from `D:\models\organized\`
4. Applies optimal parameters and required flags
5. Executes model with proper configuration

### Example from ai-router.py:
```python
"phi4-14b": {
    "name": "Phi-4 Reasoning Plus 14B Q6_K",
    "system_prompt": "system-prompt-phi4-14b.txt",  # Auto-loaded
    "temperature": 0.7,
    "special_flags": ["--jinja"],  # Auto-added
    ...
}
```

---

## Quick Navigation

### For Detailed Information
→ Read `D:\models\SYSTEM-PROMPTS-SUMMARY.md` (14KB comprehensive guide)

### For Quick Lookup
→ Read `D:\models\SYSTEM-PROMPTS-QUICK-REFERENCE.md` (quick reference card)

### For Model Research Data
→ Read `D:\models\MODEL_REFERENCE_GUIDE.md` (original research source)

### For Automated Selection
→ Run `python ai-router.py` (interactive model selector)

---

## Maintenance

### When to Update Prompts

1. **New benchmarks:** Model performance improvements discovered
2. **Parameter changes:** Updated optimal temperature/sampling settings
3. **Bug fixes:** Discovered limitations or issues
4. **Framework updates:** llama.cpp changes affecting behavior

### How to Update

1. Edit prompt file in `D:\models\organized\`
2. Update benchmark scores in `SYSTEM-PROMPTS-SUMMARY.md`
3. Update quick reference if critical warnings change
4. Test with representative queries
5. Document changes in version control

---

## File Statistics

```
Total Prompt Files:     10
  System Prompts:       8
  User Templates:       2

Total Documentation:    3
  Summary:              1 (14KB)
  Quick Reference:      1 (~10KB)
  Index:                1 (this file)

Total Size:            ~35KB (all prompts and docs)
```

---

## Version History

**v1.0** - December 8, 2024
- Initial creation of all 10 prompt files
- 8 system prompts for models with system prompt support
- 2 user templates for models without system prompt support
- Comprehensive documentation and quick reference
- Integration with ai-router.py v1.0

---

## Related Files

```
D:\models\ai-router.py                          # Main application
D:\models\MODEL_REFERENCE_GUIDE.md              # Research source
D:\models\2025-RESEARCH-SUMMARY.md              # Research findings
D:\models\HOW-TO-RUN-AI-ROUTER.md               # Usage guide
```

---

**Quick Start:** Run `python ai-router.py` for automatic model selection with optimized prompts!

---

**End of Index**