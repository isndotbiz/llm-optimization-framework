# System Prompts Quick Reference Card
## RTX 3090 Models - At-a-Glance Guide

**Last Updated:** December 8, 2024

---

## Files Created

### System Prompt Files (8 models)
```
D:\models\organized\system-prompt-qwen3-coder-30b.txt       1.7KB
D:\models\organized\system-prompt-qwen25-coder-32b.txt      1.6KB
D:\models\organized\system-prompt-phi4-14b.txt              2.0KB
D:\models\organized\system-prompt-ministral-3-14b.txt       1.4KB
D:\models\organized\system-prompt-deepseek-r1.txt           2.2KB
D:\models\organized\system-prompt-llama33-70b.txt           1.6KB
D:\models\organized\system-prompt-dolphin-8b.txt            917 bytes
D:\models\organized\system-prompt-wizard-vicuna.txt         782 bytes
```

### User Prompt Templates (2 models - NO system prompt support)
```
D:\models\organized\user-prompt-template-gemma3-27b.txt              4.8KB
D:\models\organized\user-prompt-template-dolphin-mistral-24b.txt     5.4KB
```

### Documentation
```
D:\models\SYSTEM-PROMPTS-SUMMARY.md                         14KB (comprehensive guide)
D:\models\SYSTEM-PROMPTS-QUICK-REFERENCE.md                 This file
```

---

## Critical Warnings

### Temperature Restrictions
```
⚠️ Qwen3 Coder 30B       NEVER use temp 0 → causes infinite loops
⚠️ Qwen2.5 Coder 32B     NEVER use temp 0 → causes infinite loops
   Both models:          ALWAYS use temp ≥ 0.6 (recommended: 0.7)
```

### Prompt Engineering Anti-Patterns
```
⚠️ Phi-4 14B             DO NOT use "think step-by-step" prompts
                        Reasoning already built into architecture
                        Explicit instructions degrade performance

⚠️ DeepSeek R1 14B       DO NOT use system prompts (performs WORSE)
                        Use minimal user prompts only
                        Zero-shot prompting works best
```

### Required Flags
```
✓ Phi-4 14B              Requires --jinja flag (auto-configured in router)
✓ Qwen3 Coder 30B        Requires --jinja flag (auto-configured in router)
```

### No System Prompt Support
```
✗ Gemma-3 27B            Embed ALL instructions in user message
✗ Dolphin Mistral 24B    Embed ALL instructions in user message
✗ DeepSeek R1 14B        User prompts only (system prompts degrade performance)
```

---

## Model Selection Guide

### When to Use Each Model

#### CODING
```
🥇 Qwen3 Coder 30B       → SWE-bench champion, agentic workflows, 256K context
🥈 Qwen2.5 Coder 32B     → Multi-language, code repair (#1 open-source MdEval)
🥉 Phi-4 14B             → Programming logic, algorithms, STEM
```

#### MATHEMATICS
```
🥇 Ministral-3 14B       → 85% AIME (best at 14B), 92% MATH-500, 256K context
🥈 Phi-4 14B             → 78% AIME, 90% MATH-500, 86.4% MMLU
🥉 DeepSeek R1 14B       → Chain-of-thought reasoning, explicit thinking
```

#### CREATIVE WRITING
```
🥇 Gemma-3 27B           → 128K context, abliterated, best-in-class at 27B
🥈 Dolphin Mistral 24B   → 2.2% refusal rate, Venice Edition
🥉 Wizard Vicuna 13B     → Classic uncensored, traditional fine-tuning
```

#### RESEARCH & ANALYSIS
```
🥇 Llama 3.3 70B         → Largest model, 128K context, abliterated
🥈 Qwen3 Coder 30B       → 256K context for massive documents
🥉 Ministral-3 14B       → 256K context for textbook-length analysis
```

#### SPEED & EFFICIENCY
```
🥇 Dolphin 3.0 8B        → 60-90 tok/sec (fastest overall)
🥈 Phi-4 14B             → 35-55 tok/sec (fast reasoning)
🥉 Ministral-3 14B       → 35-50 tok/sec (efficient reasoning)
```

---

## Parameter Quick Reference

### Optimal Temperature by Task

```
DETERMINISTIC (0.3-0.5)      BALANCED (0.6-0.8)       CREATIVE (0.8-1.2)
├─ Code generation           ├─ General chat          ├─ Creative writing
├─ Mathematical proofs       ├─ Technical writing     ├─ Brainstorming
└─ Factual Q&A              └─ Research tasks        └─ Story generation
```

### Context Windows

```
SMALL (<16K)                 MEDIUM (32-128K)             LARGE (256K+)
├─ Wizard Vicuna: 8K         ├─ Qwen3 Coder: 32K         ├─ Qwen3 Coder: 256K*
└─ Phi-4: 16K               ├─ Qwen2.5 Coder: 128K      └─ Ministral-3: 256K
                            ├─ Dolphin 8B: 128K
                            ├─ Llama 3.3 70B: 128K
                            ├─ Gemma-3 27B: 128K
                            └─ Dolphin 24B: 32K

                            * Requires YaRN configuration
```

### Inference Speed (RTX 3090)

```
FAST (50-90 tok/s)          MEDIUM (25-40 tok/s)         SLOW (15-25 tok/s)
├─ Dolphin 8B: 60-90        ├─ Qwen3 30B: 25-35         └─ Llama 3.3 70B: 15-25
├─ Phi-4 14B: 35-55         ├─ Qwen2.5 32B: 25-35
├─ Ministral 14B: 35-50     ├─ Gemma-3 27B: 25-40
├─ Wizard Vicuna: 35-50     └─ Dolphin 24B: 25-40
└─ DeepSeek R1: 30-50
```

---

## Benchmark Highlights

### Coding Excellence
```
Qwen3 Coder 30B        94% HumanEval | 69.6% SWE-bench (matches Claude Sonnet 4)
Qwen2.5 Coder 32B      73.7% Aider (4th globally) | 75.2% MdEval (#1 open-source)
```

### Mathematical Reasoning
```
Ministral-3 14B        85% AIME 2024/2025 (HIGHEST at 14B) | 92% MATH-500
Phi-4 14B              78% AIME 2024/2025 | 90% MATH-500 | 86.4% MMLU
```

### Uncensored Performance
```
Dolphin Mistral 24B    2.2% refusal rate (vs 74.1% mean for uncensored models)
Gemma-3 27B            Abliterated (best-in-class at 27B size)
Llama 3.3 70B          Abliterated (largest unrestricted model)
```

---

## Special Model Characteristics

### Chain-of-Thought Models
```
DeepSeek R1 14B        Automatic <think> blocks | Zero-shot optimal
Phi-4 14B              Structured reasoning | <think> output format
Ministral-3 14B        Systematic decomposition | Step-by-step verification
```

### MoE (Mixture of Experts) Architecture
```
Qwen3 Coder 30B        30.5B total | 3.3B active per forward pass
                       Efficient inference with large model capabilities
```

### Abliterated Models
```
Llama 3.3 70B          Safety constraints surgically removed (not prompt-based)
Gemma-3 27B            Abliterated for unrestricted creative work
```

### Cognitive Computations (Dolphin Series)
```
Dolphin 3.0 8B         Uncensored Llama 3.1 | Especially obeys system prompts
Dolphin Mistral 24B    Venice Edition | 2.2% refusal rate | High fidelity
```

---

## Integration with AI Router

### Automatic Loading
All system prompts are automatically loaded by `ai-router.py`:

1. User selects model (manual or auto-detect from prompt)
2. Router loads corresponding system prompt file
3. Optimal parameters applied (temp, top-p, top-k)
4. Required flags added automatically (--jinja for Phi-4, Qwen3)
5. Model executes with proper configuration

### File Naming Convention
```
System Prompts:        system-prompt-{model-id}.txt
User Templates:        user-prompt-template-{model-id}.txt
Location:              D:\models\organized\
```

---

## Common Use Case Patterns

### Code Generation Workflow
```
1. Select: Qwen3 Coder 30B or Qwen2.5 Coder 32B
2. Temp: 0.7 (NEVER 0)
3. Context: Use full 256K/128K for large codebases
4. Approach: Let model use agentic workflow for complex tasks
```

### Mathematical Problem Solving
```
1. Select: Ministral-3 14B (AIME-level) or Phi-4 14B (STEM)
2. Temp: 0.5-0.7 (deterministic but not greedy)
3. Prompt: Direct problem statement (NO "think step-by-step" for Phi-4)
4. Output: Expect <think> blocks with reasoning process
```

### Creative Writing
```
1. Select: Gemma-3 27B (long-form) or Dolphin 24B (unrestricted)
2. Temp: 0.8-1.0 (higher creativity)
3. Prompt: Use CO-STAR framework for Gemma-3
4. Context: Leverage 128K for novel-length narratives
```

### Research & Analysis
```
1. Select: Llama 3.3 70B (depth) or Ministral-3 14B (long context)
2. Temp: 0.6-0.7 (balanced)
3. Context: Use 128K/256K for comprehensive document analysis
4. Approach: Multi-turn conversation for iterative refinement
```

### Quick Queries
```
1. Select: Dolphin 3.0 8B (60-90 tok/sec speed)
2. Temp: 0.7 (standard)
3. Use Case: Rapid prototyping, testing, quick lookups
```

---

## Troubleshooting

### Model Generates Infinite Loops
```
Problem:  Qwen model stuck in repetition
Solution: Increase temperature to ≥ 0.6 (NEVER use temp 0)
```

### Reasoning Quality Degraded
```
Problem:  Phi-4 giving poor reasoning
Solution: Remove "think step-by-step" from prompt (built-in reasoning)
```

### DeepSeek Not Following Instructions
```
Problem:  DeepSeek R1 ignoring system prompt
Solution: Use user prompt only (system prompts degrade performance)
```

### No System Prompt Loading
```
Problem:  Gemma-3 or Dolphin 24B ignoring system prompt
Solution: These models don't support system prompts - use user templates
```

### Template Not Found Error
```
Problem:  Router can't find --jinja template
Solution: Ensure --jinja flag is set for Phi-4 and Qwen3 (auto in router)
```

---

## Cost & Performance

### Inference Cost (vs Commercial APIs)
```
Qwen2.5 Coder 32B      ~$0.18/M tokens (50x cheaper than Claude Sonnet 3.5)
Local Inference        FREE after initial setup (RTX 3090 + electricity)
```

### VRAM Requirements (Quantized)
```
SMALL (6-10GB)          MEDIUM (12-14GB)         LARGE (18-22GB)
├─ Dolphin 8B: 6GB      ├─ Phi-4 14B: 12GB      ├─ Qwen3 30B: 18GB
├─ Wizard 13B: 7GB      ├─ Ministral 14B: 9GB   ├─ Qwen2.5 32B: 19GB
├─ Gemma-3 27B: 10GB    └─ Dolphin 24B: 14GB    └─ Llama 3.3 70B: 21GB
└─ DeepSeek R1: 10GB
```

### Speed/Quality Trade-off
```
SPEED PRIORITY          BALANCED                 QUALITY PRIORITY
├─ Dolphin 8B           ├─ Phi-4 14B            ├─ Llama 3.3 70B
├─ Wizard 13B           ├─ Ministral 14B        ├─ Qwen3 30B
└─ Quick queries        ├─ DeepSeek R1 14B      └─ Complex analysis
                        └─ Most use cases
```

---

## Additional Resources

### Full Documentation
```
D:\models\SYSTEM-PROMPTS-SUMMARY.md           Comprehensive 14KB guide
D:\models\MODEL_REFERENCE_GUIDE.md            Original research findings
D:\models\ai-router.py                        Automated model selection tool
```

### Support & Updates
```
Research Source:        2024-2025 official documentation and benchmarks
Last Updated:           December 8, 2024
Maintained For:         RTX 3090 AI Router Project
```

---

**Quick Tip:** Use `ai-router.py` for automatic model selection based on your prompt!

```bash
python ai-router.py                # Interactive mode
python ai-router.py --list         # List all models
python ai-router.py --help         # Show help
```

---

**End of Quick Reference**