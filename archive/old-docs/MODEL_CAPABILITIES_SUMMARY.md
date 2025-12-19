# Model Capabilities Summary - Quick Reference

**Quick lookup table for model selection in ai-router.py**

---

## System Prompt Support

| ✅ SUPPORTED | ❌ NOT SUPPORTED |
|-------------|-----------------|
| Qwen 2.5 Coder 32B | Gemma 2 27B |
| DeepSeek Coder V2 Lite | |
| Llama 3.1 70B | |
| Llama 3.3 70B | |
| Mistral Large 2 123B | |
| Nemotron 70B | |
| QwQ 32B | |
| Command R 35B | |
| WizardLM 2 8x22B | |
| DBRX Instruct | |

**Note:** Gemma 2 27B requires embedding system instructions in the first user message instead.

---

## Reasoning Effort Parameter Support

**NONE of the models support OpenAI-style reasoning effort (low/medium/high)**

Only QwQ 32B has built-in reasoning capabilities via visible `<think>` tags, but this is not a controllable parameter like OpenAI's o1/o3 models.

---

## Full Parameter Support Matrix

| Model | temp | top_p | top_k | freq_pen | pres_pen | max_tok | Notes |
|-------|------|-------|-------|----------|----------|---------|-------|
| **Qwen 2.5 Coder 32B** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Temp ≥0.6 required |
| **DeepSeek Coder V2 Lite** | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | Temp 0.3 for coding |
| **Gemma 2 27B** | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | Framework-dependent |
| **Llama 3.1 70B** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Temp 0.4-0.7 |
| **Llama 3.3 70B** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Temp 0.4-0.7 |
| **Mistral Large 2 123B** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Default temp 1.0 |
| **Nemotron 70B** | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | Framework-dependent |
| **QwQ 32B** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Temp 0.6, TopP 0.95 required |
| **Command R 35B** | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ | Also: prompt_truncation |
| **WizardLM 2 8x22B** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Full support |
| **DBRX Instruct** | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | Framework-dependent |

Legend: ✅ Fully supported | ⚠️ Limited/Framework-dependent | ❌ Not supported

---

## Context Window Sizes

| Model | Context Window | Notes |
|-------|---------------|-------|
| **Qwen 2.5 Coder 32B** | 32K (128K with YaRN) | Use YaRN for >32K |
| **DeepSeek Coder V2 Lite** | 128K | Extended from 16K |
| **Gemma 2 27B** | 8K | Default configuration |
| **Llama 3.1 70B** | 128K | 16x increase from Llama 3 |
| **Llama 3.3 70B** | 128K+ | Longer than 3.1 |
| **Mistral Large 2 123B** | 128K | ~300-page book |
| **Nemotron 70B** | 128K input, 4K output | Output capped |
| **QwQ 32B** | 32K (128K with YaRN) | Enable YaRN for >8K |
| **Command R 35B** | 128K | Optimized for RAG |
| **WizardLM 2 8x22B** | 32K-64K | Varies by quantization |
| **DBRX Instruct** | 32K | Fine-grained MoE |

---

## Optimal Use Cases

| Model | Primary Use Case | Secondary Use Cases |
|-------|-----------------|---------------------|
| **Qwen 2.5 Coder 32B** | Advanced code generation | Multi-language dev, code review, architecture |
| **DeepSeek Coder V2 Lite** | Efficient coding (MoE) | 338 languages, bug fixing, math reasoning |
| **Gemma 2 27B** | General text generation | Q&A, summarization, reasoning |
| **Llama 3.1 70B** | Dialogue & tool calling | Chatbots, coding, multilingual (8 langs) |
| **Llama 3.3 70B** | Enhanced dialogue | All 3.1 use cases + improvements |
| **Mistral Large 2 123B** | Advanced reasoning | Code (80+ langs), math, multilingual (12+ langs) |
| **Nemotron 70B** | Helpfulness-optimized chat | Virtual assistants, content generation |
| **QwQ 32B** | Visible reasoning process | Graduate science, math, programming |
| **Command R 35B** | RAG & tool calling | Enterprise, long documents, multilingual |
| **WizardLM 2 8x22B** | Complex chat & agents | Multilingual, reasoning, coding |
| **DBRX Instruct** | Code, SQL, RAG | Enterprise applications, programming |

---

## Critical Configuration Notes

### Qwen 2.5 Coder 32B
- **NEVER** use temperature 0 (causes infinite loops)
- **ALWAYS** use temp ≥0.6 (preferably 0.7)
- YaRN only for contexts >32K

### DeepSeek Coder V2 Lite
- Use temp 0.3 for deterministic coding tasks
- Avoid extra spaces in prompts (causes issues)
- MoE: Only 2.4B of 16B parameters active per inference

### Gemma 2 27B
- **NO system prompt support** - embed instructions in user message
- Format: `<start_of_turn>user [instructions + question] <end_of_turn>`
- Requires 108GB VRAM for full precision; use quantized versions

### Llama 3.1 & 3.3 70B
- Optimal temp: 0.4-0.7
- Code interpreter: Add "Environment: ipython" to system prompt
- Tool definitions can go in user or system prompt (test both)
- Supports 8 languages

### Mistral Large 2 123B
- Version 2411 has improved long context and function calling
- Trained to acknowledge insufficient information
- Requires 300GB+ GPU (use 4-bit quant for ~69GB)
- 12+ languages, 80+ coding languages

### Nemotron 70B
- **NOT optimized for specialized domains** (e.g., math)
- Focus on general helpfulness
- Input: 128K tokens, Output: max 4K tokens
- Requires minimum 2x 80GB GPUs

### QwQ 32B
- **CRITICAL:** Must start output with `<think>\n`
- **NEVER** use greedy decoding (causes infinite loops)
- **ALWAYS:** temp=0.6, topP=0.95, topK=20-40
- Math: "Put final answer within \boxed{}"
- Multi-turn: Only include final answers, NOT thinking content
- Enable YaRN for inputs >8K tokens

### Command R 35B
- Specific prompt template required for RAG
- Default system prompt: "You are Command."
- Works best with Cohere's Embed + Rerank
- 10+ languages supported

### WizardLM 2 8x22B
- **MUST use Vicuna prompt format** for quality
- Required: "A chat between a curious user and an artificial intelligence assistant..."
- 141B total params (MoE), only subset active
- Multi-turn conversation support

### DBRX Instruct
- MoE: 132B total, 36B active per input
- 16 experts, activates 4 (65x more combinations than Mixtral)
- Requires ~264GB RAM
- 2-3x faster inference than non-MoE 132B models

---

## Hardware Requirements Summary

| Model | Minimum VRAM | Optimal Setup | Quantization |
|-------|--------------|---------------|--------------|
| **Qwen 2.5 Coder 32B** | 32GB+ RAM | RTX 3090 24GB | Q4_K_M (~19GB) |
| **DeepSeek Coder V2 Lite** | 16GB+ | Any modern GPU | MoE (2.4B active) |
| **Gemma 2 27B** | 108GB (FP) | A100 80GB / H100 | Q4/Q6 for consumer |
| **Llama 3.1 70B** | 70GB+ | 2x A100 | Various quants |
| **Llama 3.3 70B** | 70GB+ | 2x A100 | Various quants |
| **Mistral Large 2 123B** | 300GB+ (FP) | Multi-GPU setup | Q4 (~69GB) |
| **Nemotron 70B** | 160GB | 4x 40GB or 2x 80GB | Q4 (~42GB VRAM) |
| **QwQ 32B** | 32GB+ RAM | RTX 3090 24GB | Q4_K_M available |
| **Command R 35B** | 35GB+ | A100 / H100 | Various quants |
| **WizardLM 2 8x22B** | 141GB+ | Multi-GPU | Q4/Q6 versions |
| **DBRX Instruct** | 264GB RAM | Multi-GPU | Various quants |

---

## Recommended System Prompts (Short Versions)

### Qwen 2.5 Coder 32B
```
You are Qwen, a helpful coding assistant. Provide technically accurate, well-commented code following best practices.
```

### DeepSeek Coder V2 Lite
```
You are an expert programming assistant across 338 languages. Provide clear, efficient code with explanations.
```

### Gemma 2 27B
**N/A** - Embed in user message:
```
You are a helpful assistant. [Your actual question]
```

### Llama 3.1/3.3 70B
```
You are a helpful AI assistant. You excel at understanding context, following instructions, and using tools. Provide clear, accurate, helpful responses.
```

### Mistral Large 2 123B
```
You are Mistral Large 2 with state-of-the-art reasoning and coding capabilities. Provide thorough, well-reasoned responses. Acknowledge when you lack information.
```

### Nemotron 70B
```
You are an AI assistant trained to maximize helpfulness. Maintain context across conversations and provide accurate, well-structured responses.
```

### QwQ 32B
```
You are QwQ, a reasoning model. Show your thinking process, break down problems, verify logic, and provide clear final answers. For math: use \boxed{}.
```

### Command R 35B
```
You are Command R, specialized in RAG and tool use. Include citations, maintain accuracy, and execute multi-step tool use when needed.
```

### WizardLM 2 8x22B
**REQUIRED Vicuna format:**
```
A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.
```

### DBRX Instruct
```
You are DBRX with fine-grained MoE architecture. Excel at code, SQL, RAG, and math. Provide clear, practical solutions for production use.
```

---

## When to Use Each Model

**Code Generation (Multi-language):**
- Primary: Qwen 2.5 Coder 32B
- Alternative: DeepSeek Coder V2 Lite (more efficient)
- Enterprise: Mistral Large 2 123B, DBRX Instruct

**Advanced Reasoning:**
- Primary: QwQ 32B (visible thinking)
- Alternative: Mistral Large 2 123B
- General: WizardLM 2 8x22B

**Conversational AI:**
- Primary: Nemotron 70B (helpfulness-optimized)
- Alternative: Llama 3.1/3.3 70B
- Complex: WizardLM 2 8x22B

**RAG & Enterprise:**
- Primary: Command R 35B
- Alternative: DBRX Instruct
- Advanced: Mistral Large 2 123B

**General Purpose:**
- Primary: Gemma 2 27B
- Enhanced: Llama 3.1/3.3 70B

**Tool Calling:**
- Primary: Command R 35B
- Alternative: Llama 3.1/3.3 70B, Mistral Large 2

**Multilingual:**
- 12+ languages: Mistral Large 2 123B
- 10+ languages: Command R 35B
- 8 languages: Llama 3.1/3.3 70B

---

**For full details, see MODEL_REFERENCE_GUIDE.md**
