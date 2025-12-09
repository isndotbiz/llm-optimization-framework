# System Prompts Quick Start Guide

✅ **Status: All 13 models have system prompts configured!**

## 📁 File Structure

### RTX 3090 Models (D:\models\organized\)
| Model | File | System Prompt |
|-------|------|---------------|
| Llama 3.3 70B Abliterated | `Llama-3.3-70B-Instruct-abliterated-IQ2_S.gguf` | `Llama-3.3-70B-SYSTEM-PROMPT.txt` |
| Qwen3-Coder-30B | `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` | `Qwen3-Coder-30B-SYSTEM-PROMPT.txt` |
| Dolphin-Mistral-24B-Venice | `cognitivecomputations_Dolphin-Mistral-24B-Venice-Edition-Q4_K_M.gguf` | `Dolphin-Mistral-24B-SYSTEM-PROMPT.txt` |
| Phi-4-Reasoning-Plus ⭐ | `microsoft_Phi-4-reasoning-plus-Q6_K.gguf` | `Phi-4-Reasoning-Plus-SYSTEM-PROMPT.txt` |
| Gemma-3-27B-Abliterated ⭐ | `mlabonne_gemma-3-27b-it-abliterated-Q2_K.gguf` | `Gemma-3-27B-SYSTEM-PROMPT.txt` ⚠️ |
| Ministral-3-14B-Reasoning ⭐ | `Ministral-3-14B-Reasoning-2512-Q5_K_M.gguf` | `Ministral-3-14B-SYSTEM-PROMPT.txt` |
| DeepSeek-R1-Distill-Qwen-14B | `DeepSeek-R1-Distill-Qwen-14B-Q5_K_M.gguf` | `DeepSeek-R1-SYSTEM-PROMPT.txt` ⚠️ |
| Wizard-Vicuna-13B | `model-1fa5433f7f976911dddd6e97eda93885af20386fd9ac6b18a73a937af6205100-6.86GB.gguf` | `Wizard-Vicuna-13B-SYSTEM-PROMPT.txt` |
| Dolphin-3.0-8B | `Dolphin3.0-Llama3.1-8B-Q6_K.gguf` | `Dolphin-3.0-8B-SYSTEM-PROMPT.txt` |

### RTX 4060 Ti Models (D:\models\rtx4060ti-16gb\)
| Model | File | System Prompt |
|-------|------|---------------|
| Qwen2.5-14B-Instruct | `qwen25-14b-instruct/Qwen2.5-14B-Instruct-Q4_K_M.gguf` | `Qwen-14B-Instruct-SYSTEM-PROMPT.txt` |
| Qwen2.5-14B-Uncensored | `qwen25-14b-uncensored/Qwen2.5-14B_Uncensored_Instruct-Q4_K_M.gguf` | `Qwen-14B-Uncensored-SYSTEM-PROMPT.txt` |
| Llama-3.1-8B-Instruct | `llama31-8b-instruct/Meta-Llama-3.1-8B-Instruct-Q6_K.gguf` | `Llama-3.1-8B-SYSTEM-PROMPT.txt` |
| Qwen2.5-Coder-7B | `qwen25-coder-7b/qwen2.5-coder-7b-instruct-q5_k_m.gguf` | `Qwen-Coder-7B-SYSTEM-PROMPT.txt` |

⭐ = New models added today (2025-12-08)  
⚠️ = Special prompt handling (see notes below)

---

## 🚀 Three Ways to Use

### Method 1: Automated PowerShell Script (EASIEST)
```powershell
# Run with optimal settings
.\RUN-MODEL-WITH-PROMPT.ps1 -Model Qwen3Coder -UserPrompt "Write a Python async web scraper" -UseOptimalContext

# Examples for different models
.\RUN-MODEL-WITH-PROMPT.ps1 -Model Llama70B -UserPrompt "Explain quantum mechanics"
.\RUN-MODEL-WITH-PROMPT.ps1 -Model Phi4 -UserPrompt "Solve this equation: x^4 - 5x^2 + 4 = 0"
.\RUN-MODEL-WITH-PROMPT.ps1 -Model Gemma3 -UserPrompt "Write a cyberpunk short story"
```

**Available model names:**
- RTX 3090: `Llama70B`, `Qwen3Coder`, `DolphinVenice`, `Phi4`, `Gemma3`, `Ministral3`, `DeepSeekR1`, `WizardVicuna`, `Dolphin8B`
- RTX 4060 Ti: `Qwen14BInstruct`, `Qwen14BUncensored`, `Llama8B`, `QwenCoder7B`

### Method 2: Copy-Paste System Prompts
Each `.txt` file contains a ready-to-use system prompt. Just copy the contents when running your model manually.

```powershell
# Example with llama.cpp
llama-cli -m "D:\models\organized\Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf" `
  --system-prompt-file "D:\models\organized\Qwen3-Coder-30B-SYSTEM-PROMPT.txt" `
  -p "Write a Python web scraper" `
  --temp 0.7 --top-p 0.8 --top-k 20 --repeat-penalty 1.05 `
  -c 131072 --jinja
```

### Method 3: Check Complete Documentation
See `OPTIMIZED-SYSTEM-PROMPTS-2025-RESEARCH-BASED.txt` for:
- Complete llama.cpp commands for each model
- Detailed parameter explanations
- Research citations
- Best practices

---

## ⚠️ Special Cases

### Gemma-3-27B (NO System Prompt Support)
Gemma models **do not support traditional system prompts**. The file contains a **CO-STAR framework template** to use as a **user prompt prefix** instead:

```
Context: [Your task context]
Objective: [What you want]
Style: [Writing style]
Tone: [Desired tone]
Audience: [Target readers]
Response: [Format/length]

[Your actual prompt here]
```

**Parameters:** temp=1.0, top_k=50, min_p=0.08 (uses min_p instead of top_p)

### DeepSeek-R1 (NO System Prompt)
DeepSeek-R1 **performs worse with system prompts**. The file contains a **user prompt template** only:

```
Task: [Your question/task]

Requirements:
- Show reasoning steps naturally
- Explain your thought process
- Verify conclusions

[Your question here]
```

**Note:** Avoid explicit "think step-by-step" prompts - it has built-in chain-of-thought reasoning.

---

## 📊 Configuration Files

1. **`MODEL-PARAMETERS-QUICK-REFERENCE.json`** - Complete parameter database
   - Optimal temperature, context, sampling params for each model
   - Special flags (e.g., `--jinja` for Phi-4, Qwen models)
   - Use cases and model strengths

2. **`RUN-MODEL-WITH-PROMPT.ps1`** - Automated runner script
   - Handles all special cases automatically
   - Loads correct system prompts
   - Applies optimal parameters

3. **`OPTIMIZED-SYSTEM-PROMPTS-2025-RESEARCH-BASED.txt`** - Master documentation
   - Complete llama.cpp commands
   - Research-backed recommendations
   - Parameter tuning guidelines

---

## 🎯 Quick Parameter Guide

| Task Type | Temperature | Notes |
|-----------|-------------|-------|
| Code generation | 0.1-0.3 | Precision required |
| Math/reasoning | 0.2-0.7 | Balance creativity & accuracy |
| General chat | 0.6-0.8 | Natural conversation |
| Creative writing | 0.8-1.2 | Maximum creativity |
| Structured JSON | 0.0 | Deterministic output |

**Context optimization:** Use only what you need - each token adds ~0.24ms latency.

**Critical notes:**
- Qwen models: MUST use sampling (temp >= 0.6), NOT greedy decoding
- Phi-4: Requires `--jinja` flag
- Reasoning models: Avoid explicit "think step-by-step" prompts

---

## 📈 Model Use Cases

### RTX 3090 (Research & Heavy Lifting)
- **Llama 3.3 70B**: Best uncensored reasoning, complex research
- **Qwen3-Coder-30B**: Advanced coding (94% HumanEval), 256K context
- **Phi-4-Reasoning-Plus**: Math & logic (78% AIME 2025)
- **Ministral-3-14B**: Best reasoning at 14B (85% AIME), 256K context
- **Gemma-3-27B**: Creative writing, 128K context
- **DeepSeek-R1**: Chain-of-thought reasoning (94.3% MATH-500)
- **Dolphin-Mistral-24B**: Lowest refusal rate (2.2%)

### RTX 4060 Ti (Server & Fast Tasks)
- **Qwen2.5-14B-Instruct**: Smart daily driver with safety
- **Qwen2.5-14B-Uncensored**: Uncensored daily driver
- **Qwen2.5-Coder-7B**: Fast coding (84.8% HumanEval)
- **Llama-3.1-8B**: Production-ready, Meta official

---

## 🔗 Files Summary
- ✅ 13 individual system prompt files (`.txt`)
- ✅ Parameter reference database (`.json`)
- ✅ Automated runner script (`.ps1`)
- ✅ Master documentation (`.txt`, 51KB)
- ✅ This quick start guide (`.md`)

**All prompts use:**
- Research-optimized structures (XML where beneficial)
- Positive framing ("do this" not "don't do that")
- Model-specific capabilities and strengths
- 2025 best practices
