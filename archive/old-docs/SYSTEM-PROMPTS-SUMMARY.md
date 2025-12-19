# System Prompts Summary - RTX 3090 Models
## Comprehensive Research-Based Optimized Prompts

**Created:** December 8, 2025
**Based on:** MODEL_REFERENCE_GUIDE.md research findings
**Location:** D:\models\organized\

---

## Overview

All 10 RTX 3090 models now have optimized system prompts or user message templates based on 2024-2025 research findings. Each prompt is tailored to the model's specific strengths, limitations, and optimal use cases.

---

## System Prompt Files Created

### 1. Qwen3 Coder 30B
**File:** `system-prompt-qwen3-coder-30b.txt` (1.7KB)
**Model ID:** `qwen3-coder-30b`
**System Prompt Support:** YES

**Key Features:**
- MoE architecture optimized for agentic coding workflows
- 94% HumanEval, 69.6% SWE-bench Verified (matches Claude Sonnet 4)
- 256K context window for analyzing entire codebases
- Iterative debugging and error feedback loops

**Critical Warnings:**
- NEVER use temperature 0 (causes endless loops)
- Always use temperature ≥ 0.6 (recommended: 0.7)
- Requires `--jinja` flag for proper template handling

---

### 2. Qwen2.5 Coder 32B
**File:** `system-prompt-qwen25-coder-32b.txt` (1.6KB)
**Model ID:** `qwen25-coder-32b`
**System Prompt Support:** YES

**Key Features:**
- 73.7% on Aider benchmark (4th place, comparable to GPT-4o)
- 75.2% MdEval code repair (#1 among open-source)
- 40+ programming languages
- 128K context window

**Critical Warnings:**
- NEVER use temperature 0 (causes infinite loops)
- ALWAYS use temperature ≥ 0.6 (recommended: 0.7)
- Use YaRN rope_scaling for contexts > 32K tokens

**Cost Advantage:** ~$0.18/M tokens (50x cheaper than Claude Sonnet 3.5)

---

### 3. Phi-4 Reasoning Plus 14B
**File:** `system-prompt-phi4-14b.txt` (2.0KB)
**Model ID:** `phi4-14b`
**System Prompt Support:** YES

**Key Features:**
- 78% AIME 2024/2025 (189% improvement over base Phi-4)
- 90% MATH-500, 86.4% MMLU
- Advanced mathematical and logical reasoning
- Structured thinking process with explicit reasoning steps

**Critical Warnings:**
- DO NOT use "think step-by-step" prompts (degrades performance)
- Reasoning is already built into model architecture
- Requires `--jinja` flag for proper template handling

**Output Format:** Uses `<think>` tags for reasoning process, followed by final solution

---

### 4. Gemma-3 27B
**File:** `user-prompt-template-gemma3-27b.txt` (4.8KB)
**Model ID:** `gemma3-27b`
**System Prompt Support:** NO - User message template instead

**Key Features:**
- Best-in-class performance at 27B size
- 128K context window (competitive with 50B+ models)
- Abliterated for unrestricted creative expression
- CO-STAR framework for creative writing

**Critical Note:**
- NO system prompt support - embed all instructions in user message
- Excellent for creative writing, research, and chat
- Use temperature 0.75-1.0 for creative tasks

**Use Case:** Primary creative writing model with unrestricted capabilities

---

### 5. Ministral-3 14B Reasoning
**File:** `system-prompt-ministral-3-14b.txt` (1.4KB)
**Model ID:** `ministral-3-14b`
**System Prompt Support:** YES

**Key Features:**
- 85% AIME 2024/2025 (HIGHEST in 14B class, beats Phi-4's 78%)
- 92% MATH-500
- 256K context window for textbook-length reasoning
- Best-in-class mathematical reasoning at 14B size

**Problem-Solving Approach:**
1. Identify problem structure
2. Break into sub-problems
3. Solve with explicit reasoning
4. Verify each step
5. Synthesize complete answer
6. Final verification

---

### 6. DeepSeek R1 Distill Qwen 14B
**File:** `system-prompt-deepseek-r1.txt` (2.2KB)
**Model ID:** `deepseek-r1-14b`
**System Prompt Support:** NO - Performs WORSE with system prompts!

**Key Features:**
- Chain-of-thought reasoning model
- Automatic `<think>` block generation
- Zero-shot prompting performs best
- Minimal instruction approach

**Critical Requirements:**
- ALL instructions in USER PROMPT ONLY
- Use zero-shot (no few-shot examples - degrades performance)
- Avoid verbose instructions (minimal prompting works best)
- Exclude `<think>` blocks from multi-turn conversation history

**Template:** "Please reason step by step, and put your final answer within \boxed{}."

---

### 7. Llama 3.3 70B Abliterated
**File:** `system-prompt-llama33-70b.txt` (1.6KB)
**Model ID:** `llama33-70b`
**System Prompt Support:** YES

**Key Features:**
- 70B parameters for deep reasoning
- Abliterated (safety constraints surgically removed)
- 128K context window
- December 2024 knowledge cutoff
- Expert-level multi-domain performance

**Capabilities:**
- Academic research and philosophical analysis
- Technical writing and complex reasoning
- Unrestricted discussion of research topics
- Multi-domain synthesis

**Use Case:** Largest model for complex tasks requiring deep reasoning and unrestricted exploration

---

### 8. Dolphin 3.0 Llama 3.1 8B
**File:** `system-prompt-dolphin-8b.txt` (917 bytes)
**Model ID:** `dolphin-llama31-8b`
**System Prompt Support:** YES

**Key Features:**
- Fastest model: 60-90 tok/sec on RTX 3090
- 128K context window
- Uncensored variant of Llama 3.1 8B
- Low refusal rate despite small size
- Function calling support

**Use Case:** Speed champion for rapid iteration, testing, and quick queries

**Training:** Dataset filtered to remove alignment, bias, and censorship patterns

---

### 9. Dolphin Mistral 24B Venice Edition
**File:** `user-prompt-template-dolphin-mistral-24b.txt` (5.4KB)
**Model ID:** `dolphin-mistral-24b`
**System Prompt Support:** NO - User message template instead

**Key Features:**
- 2.2% censorship refusal rate (vs 74.1% mean for uncensored models)
- 24B parameters, 32K context window
- Especially trained to obey prompts with high fidelity
- Iteratively improved through reinforcement learning

**Critical Note:**
- NO system prompt support - embed instructions in user message
- Can use direct prompting without extensive role-setting
- Uncensored training enables direct responses

**Use Case:** Uncensored chat, creative tasks, research with minimal restrictions

---

### 10. Wizard Vicuna 13B Uncensored
**File:** `system-prompt-wizard-vicuna.txt` (782 bytes)
**Model ID:** `wizard-vicuna-13b`
**System Prompt Support:** YES

**Key Features:**
- Combines Wizard-LM instruction-following + Vicuna conversational abilities
- Traditional fine-tuning with alignment removed
- Strong general knowledge
- Good balance: helpfulness, directness, completeness
- 8K context window

**Use Case:** Classic uncensored model for general chat and creative writing

**Training:** Fine-tuned with moralizing responses removed from training data

---

### 11. Qwen2.5 14B (MLX - MacBook M4 Only)
**File:** Not created (MacBook M4 only)
**Model ID:** `qwen25-14b-mlx`
**System Prompt Support:** YES

**Note:** This model is for MacBook M4 Pro only, not RTX 3090. System prompt would be similar to Qwen2.5 Coder but optimized for general-purpose use rather than coding.

---

## Model Categories by Use Case

### Coding Excellence
1. **Qwen3 Coder 30B** - SWE-bench champion, agentic workflows
2. **Qwen2.5 Coder 32B** - Multi-language, code repair
3. **Phi-4 14B** - Programming logic and algorithms

### Mathematical Reasoning
1. **Ministral-3 14B** - AIME champion at 14B (85%)
2. **Phi-4 14B** - STEM and competitive math (78% AIME)
3. **DeepSeek R1 14B** - Chain-of-thought reasoning

### Creative Writing
1. **Gemma-3 27B** - 128K context, abliterated
2. **Dolphin Mistral 24B** - Venice Edition, 2.2% refusal
3. **Wizard Vicuna 13B** - Classic uncensored

### Large-Scale Reasoning
1. **Llama 3.3 70B** - Largest model, 128K context, abliterated
2. **Ministral-3 14B** - 256K context for textbook-length reasoning
3. **Qwen3 Coder 30B** - 256K context for massive codebases

### Speed & Efficiency
1. **Dolphin 3.0 8B** - 60-90 tok/sec, fastest overall
2. **Phi-4 14B** - 35-55 tok/sec, fast reasoning
3. **Ministral-3 14B** - 35-50 tok/sec, efficient reasoning

---

## System Prompt Design Principles

All prompts follow these research-based principles:

### 1. Model-Specific Optimization
- Leverage documented strengths from official research
- Address known limitations with explicit warnings
- Optimize parameters based on benchmark findings

### 2. Clear Role Definition
- Specific expertise areas and capabilities
- Performance metrics and benchmark scores
- Architecture advantages (MoE, context window, etc.)

### 3. Actionable Guidelines
- Response structure and formatting
- Output expectations and quality standards
- Domain-specific best practices

### 4. Critical Warnings
- Temperature restrictions (Qwen models)
- Prompt engineering anti-patterns (Phi-4, DeepSeek R1)
- Required flags and configurations

### 5. Use Case Alignment
- Coding: Production-ready, secure, maintainable
- Math/Reasoning: Systematic, verifiable, rigorous
- Creative: Original, vivid, psychologically deep
- Research: Comprehensive, factual, well-cited

---

## Special Cases & Notes

### Models WITHOUT System Prompt Support

**Gemma-3 27B:**
- Use CO-STAR framework in user message
- Embed all instructions as user prompt prefix
- Template provided in `user-prompt-template-gemma3-27b.txt`

**Dolphin Mistral 24B:**
- Embed role and guidelines in user message
- Can also use direct prompting (uncensored training)
- Template provided in `user-prompt-template-dolphin-mistral-24b.txt`

**DeepSeek R1 14B:**
- Performs WORSE with system prompts
- Use minimal, zero-shot user prompts only
- Template: "Please reason step by step, and put your final answer within \boxed{}."

### Temperature Restrictions

**Qwen Models (Qwen3 30B, Qwen2.5 32B):**
- NEVER use temperature 0
- ALWAYS use ≥ 0.6 (recommended: 0.7)
- Causes infinite loops and repetition at temp 0

### Required Flags

**Phi-4 14B:**
- Requires `--jinja` flag for proper template handling
- Already configured in ai-router.py

**Qwen3 Coder 30B:**
- Requires `--jinja` flag
- Already configured in ai-router.py

---

## Integration with AI Router

All system prompts are automatically loaded by `ai-router.py` when models are selected. The router:

1. Detects model from selection
2. Loads corresponding system prompt file
3. Applies optimal parameters (temp, top-p, top-k)
4. Includes required flags automatically
5. Executes with proper configuration

### File Naming Convention

System prompts follow this naming pattern:
```
system-prompt-{model-id}.txt
```

User templates for non-system-prompt models:
```
user-prompt-template-{model-id}.txt
```

### Location
All prompts stored in: `D:\models\organized\`

---

## Prompt Maintenance

### When to Update Prompts

1. **New Research Findings:** Model benchmark improvements or new capabilities
2. **Parameter Changes:** Updated optimal temperature/sampling settings
3. **Bug Fixes:** Discovered issues or limitations
4. **Framework Updates:** llama.cpp or MLX changes affecting behavior

### Editing Guidelines

- Maintain structured format (role, capabilities, guidelines, warnings)
- Include specific benchmark scores and metrics
- Add critical warnings prominently
- Test changes with representative queries
- Document any deviations from research findings

---

## Performance Optimization

### Context Window Usage

**Small Context (<8K):**
- Wizard Vicuna 13B: 8K
- Phi-4 14B: 16K

**Medium Context (32-128K):**
- Qwen3 Coder 30B: 32K (extendable to 256K)
- Qwen2.5 Coder 32B: 128K
- Dolphin 3.0 8B: 128K
- Llama 3.3 70B: 128K
- Gemma-3 27B: 128K
- Dolphin Mistral 24B: 32K

**Large Context (256K+):**
- Qwen3 Coder 30B: 256K (with YaRN)
- Ministral-3 14B: 256K

### Temperature Recommendations

**Deterministic/Technical (0.3-0.5):**
- Code generation
- Mathematical proofs
- Factual Q&A

**Balanced (0.6-0.8):**
- General conversation
- Technical writing
- Research tasks

**Creative (0.8-1.2):**
- Creative writing
- Brainstorming
- Story generation

---

## Benchmark Performance Summary

### Coding
- **Qwen3 Coder 30B:** 94% HumanEval, 69.6% SWE-bench
- **Qwen2.5 Coder 32B:** 73.7% Aider, 75.2% MdEval

### Mathematical Reasoning
- **Ministral-3 14B:** 85% AIME, 92% MATH-500
- **Phi-4 14B:** 78% AIME, 90% MATH-500

### General Knowledge
- **Phi-4 14B:** 86.4% MMLU
- **Ministral-3 14B:** 84% MMLU

### Refusal Rate (Lower = Better)
- **Dolphin Mistral 24B:** 2.2% (best uncensored)
- **Dolphin 3.0 8B:** Low (specific % not documented)

---

## Research Sources

All prompts based on official documentation and 2024-2025 research:

- Qwen Documentation (Hugging Face)
- Microsoft Phi-4 Technical Report
- Mistral AI Official Releases
- DeepSeek Research Papers
- Meta Llama Documentation
- Cognitive Computations (Dolphin series)
- Venice.ai Optimization Research

**Last Updated:** December 8, 2024
**Document Version:** 1.0
**Maintained for:** RTX 3090 AI Router Project

---

## Quick Reference

| Model | Prompt File | System Prompt | Temp | Context | Speed | Best For |
|-------|-------------|---------------|------|---------|-------|----------|
| Qwen3 30B | system-prompt-qwen3-coder-30b.txt | YES | 0.7 | 256K | 25-35 | SWE-bench, agentic coding |
| Qwen2.5 32B | system-prompt-qwen25-coder-32b.txt | YES | 0.7 | 128K | 25-35 | Multi-lang code, repair |
| Phi-4 14B | system-prompt-phi4-14b.txt | YES | 0.7 | 16K | 35-55 | STEM, math reasoning |
| Gemma-3 27B | user-prompt-template-gemma3-27b.txt | NO | 0.9 | 128K | 25-40 | Creative writing |
| Ministral 14B | system-prompt-ministral-3-14b.txt | YES | 0.7 | 256K | 35-50 | AIME-level math |
| DeepSeek R1 14B | system-prompt-deepseek-r1.txt | NO | 0.7 | 32K | 30-50 | Chain-of-thought |
| Llama 3.3 70B | system-prompt-llama33-70b.txt | YES | 0.7 | 128K | 15-25 | Large-scale reasoning |
| Dolphin 8B | system-prompt-dolphin-8b.txt | YES | 0.7 | 128K | 60-90 | Speed champion |
| Dolphin 24B | user-prompt-template-dolphin-mistral-24b.txt | NO | 0.8 | 32K | 25-40 | Uncensored chat |
| Wizard 13B | system-prompt-wizard-vicuna.txt | YES | 0.8 | 8K | 35-50 | General uncensored |

---

**End of Document**