# Enhanced Smart Model Selection - Example Output

## Overview

The enhanced ModelSelector system provides:
- **Confidence Scoring**: Shows how confident the system is about category detection
- **Visual Confidence Bars**: Easy-to-read visual representation of confidence
- **Top 3 Recommendations**: Shows alternative models for the detected use case
- **Preference Learning**: Remembers and applies your model preferences
- **Detailed Explanations**: Explains why a particular model was selected

---

## Example 1: Coding Task

### User Input:
```
Write a Python function to calculate fibonacci numbers
```

### System Output:
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

[MODEL INFORMATION displayed...]

Save Qwen3 Coder 30B Q4_K_M as preferred model for coding tasks? [y/N]:
```

---

## Example 2: Math/Reasoning Task

### User Input:
```
Solve this complex math equation: 2x^2 + 5x - 3 = 0
```

### System Output:
```
╔══════════════════════════════════════════════════════════════╗
║  SMART MODEL SELECTION RESULTS
╚══════════════════════════════════════════════════════════════╝

Detected Category: MATH
Confidence Score: ██████████ 100%

Why this selection?
Selected math model with high confidence (100%) - detected math keywords
like 'calculate', 'equation', 'solve'

Selected Model: Phi-4 Reasoning Plus 14B Q6_K

Model Recommendations (Top 3):
────────────────────────────────────────────────────────────

1. Phi-4 Reasoning Plus 14B Q6_K
   Category: math
   Confidence: ██████████ 100%
   Math, reasoning, STEM, logical analysis

2. Ministral-3 14B Reasoning Q5_K_M
   Category: reasoning
   Confidence: ██████░░░ 62%
   Complex reasoning, problem solving, analysis

3. DeepSeek R1 Distill Qwen 14B Q5_K_M
   Category: reasoning
   Confidence: ██████░░░ 62%
   Advanced reasoning, research, complex analysis
────────────────────────────────────────────────────────────

[MODEL INFORMATION displayed...]

Save Phi-4 Reasoning Plus 14B Q6_K as preferred model for math tasks? [y/N]:
```

---

## Example 3: Creative Writing Task

### User Input:
```
Write a creative short story about a robot learning to feel emotions
```

### System Output:
```
╔══════════════════════════════════════════════════════════════╗
║  SMART MODEL SELECTION RESULTS
╚══════════════════════════════════════════════════════════════╝

Detected Category: CREATIVE
Confidence Score: ██████████ 100%

Why this selection?
Selected creative model with high confidence (100%) - detected creative
keywords like 'story', 'write', 'imagine'

Selected Model: Gemma 3 27B Q2_K (Abliterated)

Model Recommendations (Top 3):
────────────────────────────────────────────────────────────

1. Gemma 3 27B Q2_K (Abliterated)
   Category: creative
   Confidence: ██████████ 100%
   Uncensored chat, creative writing, research

2. Dolphin Mistral 24B Venice Q4_K_M
   Category: creative
   Confidence: ██████████ 100%
   Uncensored chat, creative tasks, roleplay
────────────────────────────────────────────────────────────

[MODEL INFORMATION displayed...]

Save Gemma 3 27B Q2_K (Abliterated) as preferred model for creative tasks? [y/N]:
```

---

## Example 4: Research Task

### User Input:
```
Research and explain how quantum computing works
```

### System Output:
```
╔══════════════════════════════════════════════════════════════╗
║  SMART MODEL SELECTION RESULTS
╚══════════════════════════════════════════════════════════════╝

Detected Category: RESEARCH
Confidence Score: ██████████ 100%

Why this selection?
Selected research model with high confidence (100%) - detected research
keywords like 'explain', 'summarize', 'compare'

Selected Model: Llama 3.3 70B Instruct IQ2_S

Model Recommendations (Top 3):
────────────────────────────────────────────────────────────

1. Llama 3.3 70B Instruct IQ2_S
   Category: research
   Confidence: ██████████ 100%
   Large-scale reasoning, research, uncensored tasks

2. Ministral-3 14B Reasoning Q5_K_M
   Category: research
   Confidence: ██████████ 100%
   Complex reasoning, problem solving, analysis
────────────────────────────────────────────────────────────

[MODEL INFORMATION displayed...]

Save Llama 3.3 70B Instruct IQ2_S as preferred model for research tasks? [y/N]:
```

---

## Example 5: Low Confidence / Ambiguous Prompt

### User Input:
```
Tell me something interesting
```

### System Output:
```
╔══════════════════════════════════════════════════════════════╗
║  SMART MODEL SELECTION RESULTS
╚══════════════════════════════════════════════════════════════╝

Detected Category: GENERAL
Confidence Score: ███░░░░░░░ 30%

Why this selection?
Selected general model with low confidence (30%) - no specific category
detected, using general-purpose model

Selected Model: Dolphin 3.0 Llama 3.1 8B Q6_K

Model Recommendations (Top 3):
────────────────────────────────────────────────────────────

1. Dolphin 3.0 Llama 3.1 8B Q6_K
   Category: general
   Confidence: ███░░░░░░░ 30%
   Fast general tasks, uncensored chat, quick assistance
────────────────────────────────────────────────────────────

[MODEL INFORMATION displayed...]

Run this model? [Y/n]:
```

*Note: With low confidence (< 60%), the system does NOT prompt to save preferences*

---

## Preference Learning Example

### After saving a preference:

```
User selects: "Yes, save this preference"

✓ Preference saved! This model will be auto-selected for future coding tasks.
```

### Next time a coding task is detected:

```
Detected Category: CODING
Confidence Score: ██████████ 100%

Why this selection?
Selected coding model with high confidence (100%) - detected code-related
keywords like 'function', 'debug', 'implement'

Selected Model: Qwen2.5 Coder 32B Q4_K_M [USER PREFERENCE]
```

The system now automatically selects the user's preferred model for that category.

---

## Preference Storage

Preferences are stored in: `D:\models\.ai-router-preferences.json`

Example file:
```json
{
  "coding": "qwen25-coder-32b",
  "math": "phi4-14b",
  "creative": "gemma3-27b"
}
```

---

## Confidence Level Indicators

- **High Confidence (≥70%)**: Green bar ██████████
- **Medium Confidence (40-69%)**: Yellow bar █████░░░░░
- **Low Confidence (<40%)**: Red bar ███░░░░░░░

---

## Key Features Demonstrated

1. **Multi-Category Detection**: System can detect multiple relevant categories
2. **Weighted Scoring**: High/medium/low keywords contribute different confidence levels
3. **Smart Normalization**: Scores normalized to 0-100% range
4. **Preference Learning**: Remembers user choices for each category
5. **Fallback Logic**: Always provides a sensible default
6. **Visual Feedback**: Easy-to-read confidence bars and color coding
7. **Explanations**: Clear reasoning about why each model was selected
