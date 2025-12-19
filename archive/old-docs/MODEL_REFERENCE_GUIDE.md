# AI Model Reference Guide - RTX 3090 Setup
## Comprehensive Capabilities & Limitations Documentation

**Last Updated:** December 2024
**Based on:** Official documentation, model cards, and 2024-2025 research

---

## Table of Contents
1. [Qwen 2.5 Coder 32B Instruct](#qwen-25-coder-32b-instruct)
2. [DeepSeek Coder V2 Lite Instruct](#deepseek-coder-v2-lite-instruct)
3. [Gemma 2 27B Instruct](#gemma-2-27b-instruct)
4. [Llama 3.1 70B Instruct](#llama-31-70b-instruct)
5. [Llama 3.3 70B Instruct](#llama-33-70b-instruct)
6. [Mistral Large 2 123B Instruct](#mistral-large-2-123b-instruct)
7. [Nemotron 70B Instruct](#nemotron-70b-instruct)
8. [QwQ 32B Preview](#qwq-32b-preview)
9. [Command R 35B](#command-r-35b)
10. [WizardLM 2 8x22B](#wizardlm-2-8x22b)
11. [DBRX Instruct](#dbrx-instruct)
12. [Quick Comparison Table](#quick-comparison-table)

---

## 1. Qwen 2.5 Coder 32B Instruct

### System Prompt Support
**YES** - Fully supported

### Reasoning Effort Parameter
**NONE** - Does not support reasoning effort levels

### Supported Parameters
| Parameter | Support | Range/Values | Notes |
|-----------|---------|--------------|-------|
| `temperature` | ✅ Yes | 0.0-2.0 | **CRITICAL: Never use 0 (causes loops). Recommended: 0.7** |
| `top_p` | ✅ Yes | 0.0-1.0 | Default: 0.9 |
| `top_k` | ✅ Yes | 1-100+ | Default: 40 |
| `frequency_penalty` | ✅ Yes | -2.0 to 2.0 | Default: 0 |
| `presence_penalty` | ✅ Yes | -2.0 to 2.0 | Default: 0 |
| `max_tokens` | ✅ Yes | 1-131072 | - |

### Context Window
- **Default:** 32,768 tokens
- **Extended:** Up to 131,072 tokens (128K) with YaRN rope_scaling configuration
- **Note:** For inputs >32,768 tokens, enable YaRN with rope_scaling configuration

### Optimal Use Case
**Advanced Code Generation & Multi-Language Development**
- Code generation, repair, and refactoring
- Multi-language code understanding (40+ languages)
- Code completion and infilling
- Architecture design and code review
- Technical documentation generation

### Recommended System Prompt
```
You are Qwen, created by Alibaba Cloud. You are a helpful coding assistant specialized in generating high-quality, efficient, and well-documented code across multiple programming languages. Your responses should be:
- Technically accurate with proper syntax
- Well-commented and explained
- Following best practices and design patterns
- Optimized for readability and maintainability
```

### Special Requirements/Limitations
- **Temperature:** Must be ≥0.6 (preferably 0.7) to avoid infinite loops
- **YaRN Configuration:** Only add rope_scaling when processing long contexts >32K
- **Deployment:** Use vLLM for optimal performance
- **Hardware:** Requires 32GB+ RAM for full model; quantized versions available for lower specs
- **Cost:** Approximately $0.18/$0.18 M tok/s (50x cheaper than Claude Sonnet 3.5)

### Benchmark Scores
- **Aider Code Editing:** 73.7% (4th place, comparable to GPT-4o)
- **McEval:** 65.9 (40+ programming languages)
- **MdEval:** 75.2 (code repair - #1 among open-source models)
- **HumanEval-Infilling:** SOTA performance

---

## 2. DeepSeek Coder V2 Lite Instruct

### System Prompt Support
**YES** - Fully supported via chat template

### Reasoning Effort Parameter
**NONE** - Does not support reasoning effort levels

### Supported Parameters
| Parameter | Support | Range/Values | Notes |
|-----------|---------|--------------|-------|
| `temperature` | ✅ Yes | 0.0-2.0 | **Recommended: 0.3 for coding tasks** |
| `top_p` | ✅ Yes | 0.0-1.0 | Default: 0.9 |
| `top_k` | ✅ Yes | 1-100+ | Not commonly used in official examples |
| `frequency_penalty` | ⚠️ Limited | - | Not in official examples |
| `presence_penalty` | ⚠️ Limited | - | Not in official examples |
| `max_tokens` | ✅ Yes | 1-128000 | max_new_tokens parameter |

### Context Window
**128,000 tokens** (extended from 16K in previous version)

### Optimal Use Case
**Efficient Code Generation with MoE Architecture**
- Code generation and completion
- Fill-in-the-middle code tasks
- Bug fixing and refactoring
- Mathematical reasoning
- Real-world code generation scenarios

### Recommended System Prompt
```
You are an expert programming assistant powered by DeepSeek Coder. You excel at understanding and generating code across 338 programming languages. Provide clear, efficient, and well-structured code solutions with explanations. Focus on:
- Correct syntax and best practices
- Clear explanations of your approach
- Consideration of edge cases
- Performance optimization where applicable
```

### Special Requirements/Limitations
- **MoE Architecture:** 16B total parameters, only 2.4B active per inference (very efficient)
- **Programming Languages:** Supports 338 languages (expanded from 86)
- **Temperature:** Use lower values (0.3) for deterministic coding tasks
- **Spaces in Prompts:** Avoid extra spaces (can cause issues on 16B-Lite model)
- **License:** Permissive license allows commercial use

### Benchmark Scores
- **Aider Benchmark:** 73.7% accuracy
- **LiveCodeBench:** 43.4% (real-world code generation)
- **Context Length:** Validated up to 128K via NIAH testing

---

## 3. Gemma 2 27B Instruct

### System Prompt Support
**NO** - Does not support traditional system role
- **Alternative:** Include system-level instructions in the first user message
- Model instruction-following capabilities allow effective interpretation without separate system role

### Reasoning Effort Parameter
**NONE** - Does not support reasoning effort levels

### Supported Parameters
| Parameter | Support | Range/Values | Notes |
|-----------|---------|--------------|-------|
| `temperature` | ✅ Yes | 0.0-2.0 | Common: 0.75-1.0 |
| `top_p` | ✅ Yes | 0.0-1.0 | Common: 0.95-1.0 |
| `top_k` | ✅ Yes | 1-100+ | Common: 40-50 |
| `frequency_penalty` | ⚠️ Limited | - | Framework-dependent |
| `presence_penalty` | ⚠️ Limited | - | Framework-dependent |
| `max_tokens` | ✅ Yes | 1-8192 | - |

### Context Window
**8,192 tokens** (default configuration)

### Optimal Use Case
**General-Purpose Text Generation & Reasoning**
- Question answering
- Summarization
- Reasoning tasks
- Fast responses and chat
- General queries
- Environments with limited resources (laptop, desktop, cloud)

### Recommended System Prompt
**N/A** - Embed instructions in first user message instead:
```
User: You are a helpful AI assistant specialized in [domain]. Only reply like [persona/style]. [Your actual question/task]
```

### Special Requirements/Limitations
- **NO System Prompt:** Must use user message for all instructions
- **Chat Template:** Uses `<bos><start_of_turn>user ... <end_of_turn><start_of_turn>model` format
- **Hardware:** Designed for single TPU host, NVIDIA A100 80GB, or H100
- **VRAM:** 108.3GB for full precision model with 8K context
- **Quantization:** Use quantized versions (Q4_K_M, Q6_K) for consumer hardware
- **Frameworks:** Compatible with Transformers, JAX, PyTorch, TensorFlow, vLLM, Ollama

### Benchmark Scores
- **Performance:** Best in class for 27B size
- **Comparison:** Competitive with models 2x its size
- Specific benchmark numbers vary by task and version

---

## 4. Llama 3.1 70B Instruct

### System Prompt Support
**YES** - Fully supported

### Reasoning Effort Parameter
**NONE** - Does not support reasoning effort levels

### Supported Parameters
| Parameter | Support | Range/Values | Notes |
|-----------|---------|--------------|-------|
| `temperature` | ✅ Yes | 0.0-2.0 | **Recommended: 0.4-0.7** |
| `top_p` | ✅ Yes | 0.0-1.0 | Default varies by provider |
| `top_k` | ✅ Yes | 1-100+ | Supported |
| `frequency_penalty` | ✅ Yes | -2.0 to 2.0 | Supported |
| `presence_penalty` | ✅ Yes | -2.0 to 2.0 | Supported |
| `max_tokens` | ✅ Yes | 1-128000 | Per run limit |

### Context Window
**128,000 tokens** (16x increase from Llama 3 models)

### Optimal Use Case
**Large-Scale AI Native Applications & Multilingual Dialogue**
- Chatbots and conversational AI
- Coding assistants
- Tool calling and function execution
- Multilingual dialogue (8 languages)
- Complex instruction-following tasks
- Applications combining conversation and tool calling

### Recommended System Prompt
```
You are a helpful AI assistant powered by Meta Llama 3.1. You excel at understanding context, following instructions, and providing accurate, helpful responses. You can use tools and maintain coherent multi-turn conversations. Your responses should be:
- Clear and well-structured
- Contextually appropriate
- Accurate and informative
- Helpful and user-focused
```

### Special Requirements/Limitations
- **Languages:** English, German, French, Italian, Portuguese, Hindi, Spanish, Thai
- **Tool Calling:** Built-in support for JSON tool calling (tool definitions in user or system prompt)
- **Code Interpreter:** Triggered by "Environment: ipython" in system prompt
- **Built-in Tools:** Brave Search (web), Wolfram Alpha (math)
- **Architecture:** Auto-regressive with optimized transformer, Grouped-Query Attention (GQA)
- **Response Limit:** Some deployments cap responses at 4,000 tokens per run

### Benchmark Scores
- Performance comparable to leading proprietary models
- Strong multilingual capabilities
- Excellent for dialogue and tool use scenarios

---

## 5. Llama 3.3 70B Instruct

### System Prompt Support
**YES** - Fully supported

### Reasoning Effort Parameter
**NONE** - Does not support reasoning effort levels

### Supported Parameters
| Parameter | Support | Range/Values | Notes |
|-----------|---------|--------------|-------|
| `temperature` | ✅ Yes | 0.0-2.0 | **Recommended: 0.4-0.7** |
| `top_p` | ✅ Yes | 0.0-1.0 | Default varies by provider |
| `top_k` | ✅ Yes | 1-100+ | Supported |
| `frequency_penalty` | ✅ Yes | -2.0 to 2.0 | Supported |
| `presence_penalty` | ✅ Yes | -2.0 to 2.0 | Supported |
| `max_tokens` | ✅ Yes | 1-128000+ | Context-dependent |

### Context Window
**128,000+ tokens** (longer than 3.1, exact number may vary)

### Optimal Use Case
**Enhanced Version of 3.1 with Latest Post-Training Techniques**
- All Llama 3.1 use cases plus improvements
- Chatbots and coding assistants
- Tool calling applications
- Multilingual dialogue (8 languages)
- Complex instruction-following

### Recommended System Prompt
```
You are a helpful AI assistant powered by Meta Llama 3.3. You represent the latest advancements in post-training techniques. You excel at understanding context, following instructions, and providing accurate, helpful responses. You can use tools and maintain coherent multi-turn conversations. Focus on:
- Clear and precise communication
- Contextual awareness
- Accurate information
- Helpful and actionable advice
```

### Special Requirements/Limitations
- **Release Date:** December 6, 2024
- **Languages:** English, German, French, Italian, Portuguese, Hindi, Spanish, Thai
- **Architecture:** Auto-regressive with optimized transformer, Grouped-Query Attention (GQA)
- **Tool Calling:** Built-in support (same as 3.1)
- **Supersedes:** Instruction-tuned Llama 3.1 70B model
- **Official Docs:** https://www.llama.com/docs/overview

### Benchmark Scores
- Improved over Llama 3.1 70B
- Latest post-training techniques applied
- Specific benchmarks available in official documentation

---

## 6. Mistral Large 2 123B Instruct

### System Prompt Support
**YES** - Fully supported (improved in 2411 version)

### Reasoning Effort Parameter
**NONE** - Does not support reasoning effort levels

### Supported Parameters
| Parameter | Support | Range/Values | Notes |
|-----------|---------|--------------|-------|
| `temperature` | ✅ Yes | 0.0-2.0 | Default: 1.0 |
| `top_p` | ✅ Yes | 0.0-1.0 | Supported |
| `top_k` | ✅ Yes | 1-100+ | Supported |
| `frequency_penalty` | ✅ Yes | -2.0 to 2.0 | Supported |
| `presence_penalty` | ✅ Yes | -2.0 to 2.0 | Supported |
| `max_tokens` | ✅ Yes | 1-128000 | - |

### Context Window
**128,000 tokens** (128K)

### Optimal Use Case
**Advanced Reasoning, Code Generation, and Multilingual Tasks**
- Code generation, completion, debugging (80+ languages)
- Complex math problems with explanations
- Advanced reasoning and logical analysis
- Question answering and text analysis
- Agentic capabilities with function calling
- RAG applications with strong context adherence
- Multilingual support (12+ languages)

### Recommended System Prompt
```
You are Mistral Large 2, an advanced AI assistant with state-of-the-art reasoning, knowledge, and coding capabilities. You excel at understanding complex problems and providing clear, accurate solutions. Your strengths include:
- Advanced mathematical and logical reasoning
- Code generation across 80+ programming languages
- Multilingual communication
- Function calling and tool use
- Deep contextual understanding

Provide thorough, well-reasoned responses while acknowledging when you lack sufficient information.
```

### Special Requirements/Limitations
- **Versions:** 2407 and 2411 (2411 has improved long context, function calling, system prompt support)
- **Languages:** English, French, German, Spanish, Italian, Portuguese, Arabic, Hindi, Russian, Chinese, Japanese, Korean
- **Coding Languages:** 80+ including Python, Java, C, C++, JavaScript, Bash, Swift, Fortran
- **Function Calling:** Best-in-class agentic capabilities with native function calling and JSON output
- **Hallucination Reduction:** Trained to acknowledge insufficient information
- **Hardware:** Requires 300GB+ GPU RAM for full model; 4-bit quantization reduces to ~69GB
- **License:** Mistral Research License (non-commercial use)

### Benchmark Scores
- **vs Llama 3.1 405B:** Outperforms on code and math despite 3x fewer parameters
- **vs GPT-4o, Claude 3 Opus, Llama 3 405B:** Performs on par
- Strong performance on reasoning, coding, and multilingual benchmarks

---

## 7. Nemotron 70B Instruct

### System Prompt Support
**YES** - Fully supported

### Reasoning Effort Parameter
**NONE** - Does not support reasoning effort levels

### Supported Parameters
| Parameter | Support | Range/Values | Notes |
|-----------|---------|--------------|-------|
| `temperature` | ✅ Yes | 0.0-2.0 | Default varies |
| `top_p` | ✅ Yes | 0.0-1.0 | Supported |
| `top_k` | ✅ Yes | 1-100+ | Supported |
| `frequency_penalty` | ⚠️ Limited | - | Framework-dependent |
| `presence_penalty` | ⚠️ Limited | - | Framework-dependent |
| `max_tokens` | ✅ Yes | 1-4000 | Output limit: 4K tokens |

### Context Window
- **Input:** Up to 131,072 tokens (128K)
- **Output:** Maximum 4,000 tokens per response

### Optimal Use Case
**Helpfulness-Optimized Conversational AI**
- Conversational AI and sophisticated chatbots
- Virtual assistants
- Content generation and writing assistance
- Question answering and information retrieval
- Educational applications
- Complex instruction-following tasks
- Multi-turn contextual conversations

### Recommended System Prompt
```
You are an AI assistant powered by NVIDIA Llama 3.1 Nemotron 70B, specifically trained to maximize helpfulness in responses. You excel at:
- Understanding and following complex instructions
- Maintaining context across long conversations
- Providing accurate, helpful, and well-structured responses
- Adapting tone and style to user needs
- Generating high-quality content

Focus on being maximally helpful while maintaining accuracy and relevance.
```

### Special Requirements/Limitations
- **Base Model:** Built on Llama 3.1 70B, customized by NVIDIA via RLHF (REINFORCE)
- **Training:** Used Llama-3.1-Nemotron-70B-Reward and HelpSteer2-Preference prompts
- **NOT Optimized For:** Specialized domains like math (general helpfulness focus)
- **Hardware Requirements:**
  - Production: NVIDIA A100 (80GB) or H100
  - Minimum: 4x 40GB or 2x 80GB NVIDIA GPUs
  - Storage: 150GB+ free disk space
  - RAM: 256GB+ system RAM recommended
  - Cost-Effective: 2x RTX 3090 (64GB total) for 4-bit quantization
- **Deployment:** Available via Hugging Face, build.nvidia.com (100K free API calls)

### Benchmark Scores
- **Arena Hard:** 85.0
- **AlpacaEval 2 LC:** 57.6
- **GPT-4-Turbo MT-Bench:** 8.98
- **ChatBot Arena Elo:** 1267 (±7) - Rank 9 (as of Oct 24, 2024)
- **#1 Position:** All three automatic alignment benchmarks (as of Oct 1, 2024)
- **Comparison:** Edges out GPT-4o and Claude 3.5 Sonnet on alignment benchmarks

---

## 8. QwQ 32B Preview

### System Prompt Support
**YES** - Supported (with special considerations for thinking mode)

### Reasoning Effort Parameter
**NONE** - Instead uses explicit thinking mode
- Model generates visible reasoning process via `<think>` tags
- Not a parameter like OpenAI's reasoning effort, but built into model behavior

### Supported Parameters
| Parameter | Support | Range/Values | Notes |
|-----------|---------|--------------|-------|
| `temperature` | ✅ Yes | 0.0-2.0 | **CRITICAL: Use 0.6, NOT greedy decoding** |
| `top_p` | ✅ Yes | 0.0-1.0 | **Recommended: 0.95** |
| `top_k` | ✅ Yes | 1-100+ | **Recommended: 20-40** |
| `frequency_penalty` | ✅ Yes | -2.0 to 2.0 | Supported |
| `presence_penalty` | ✅ Yes | -2.0 to 2.0 | Supported |
| `max_tokens` | ✅ Yes | 1-131072 | Use max_completion_tokens |
| `repetition_penalty` | ✅ Yes | 0.0-2.0 | Supported |
| `min_p` | ✅ Yes | 0.0-1.0 | Supported |

### Context Window
- **Default:** 32,000 tokens
- **Extended:** 131,072 tokens (128K) with YaRN configuration
- **For >8,192 tokens:** Enable YaRN with rope_scaling (factor: 4.0, type: "yarn")

### Optimal Use Case
**Advanced Reasoning with Visible Thinking Process**
- Graduate-level scientific reasoning
- Mathematical problem-solving
- Programming and code generation
- Complex logic puzzles
- Multi-step reasoning tasks
- Agentic applications with tool use
- Tasks requiring transparent reasoning

### Recommended System Prompt
```
You are QwQ, a reasoning model capable of deep thinking and step-by-step analysis. When solving problems:
- Show your reasoning process explicitly
- Break down complex problems into steps
- Verify your logic at each stage
- Consider alternative approaches
- Provide clear final answers

For math problems, put your final answer within \boxed{}.
For multiple-choice questions, show your choice in the answer field with only the choice letter.
```

### Special Requirements/Limitations
- **CRITICAL: Enforce Thinking Output:** Ensure model starts with `<think>\n` to prevent quality degradation
- **NO Greedy Decoding:** Temperature=0.6, TopP=0.95 required to avoid infinite repetitions
- **TopK Range:** Use 20-40 to filter rare tokens while maintaining diversity
- **Multi-turn:** Historical output should ONLY include final answers, NOT thinking content
- **Task-Specific Prompting:**
  - Math: "Please reason step by step, and put your final answer within \boxed{}."
  - Multiple-choice: "Please show your choice in the answer field with only the choice letter."
- **Long Inputs:** Enable YaRN for inputs >8,192 tokens
- **Thinking Conciseness:** Can prompt model to be more concise; affects answer quality
- **max_completion_tokens:** Increase to give sufficient reasoning space
- **Architecture:** Built on Qwen2.5-32B (32.5B parameters)
- **License:** Apache 2.0

### Benchmark Scores
- **GPQA (Graduate-level science):** 65.2%
- **AIME (Mathematical problems):** 50.0%
- **MATH-500:** 90.6%
- **LiveCodeBench (Programming):** 50.0%
- **Comparison:** Competitive with DeepSeek-R1, o1-mini

---

## 9. Command R 35B

### System Prompt Support
**YES** - Fully supported (called "preamble")
- Default: "You are Command."
- Supports custom system preambles for specialized use cases
- `use_default_system_prompt` parameter available (boolean)

### Reasoning Effort Parameter
**NONE** - Does not support reasoning effort levels

### Supported Parameters
| Parameter | Support | Range/Values | Notes |
|-----------|---------|--------------|-------|
| `temperature` | ✅ Yes | 0.0-2.0 | Supported |
| `top_p` | ✅ Yes | 0.0-1.0 | Supported |
| `top_k` | ⚠️ Limited | - | Not in primary documentation |
| `frequency_penalty` | ✅ Yes | -2.0 to 2.0 | Reduces repetitiveness proportionally |
| `presence_penalty` | ✅ Yes | -2.0 to 2.0 | Reduces repetitiveness equally |
| `max_tokens` | ✅ Yes | 1-128000 | - |
| `prompt_truncation` | ✅ Yes | AUTO_PRESERVE_ORDER | Manages long contexts |

### Context Window
**128,000 tokens** (128K)

### Optimal Use Case
**RAG, Tool Calling, and Enterprise Applications**
- Retrieval-augmented generation (RAG) at production scale
- Zero-shot multi-step tool use
- Function calling and API integration
- Long document processing
- Complex, context-rich queries
- Enterprise-level deployments
- Multilingual applications (10+ languages)

### Recommended System Prompt
```
You are Command R, an AI assistant specialized in retrieval-augmented generation and tool use. When working with documents:
- Generate responses based on supplied document snippets
- Include grounding spans (citations) indicating sources
- Maintain accuracy and context adherence

When using tools:
- Follow zero-shot multi-step tool use patterns
- Execute functions based on provided schemas
- Integrate results into coherent responses

Provide clear, accurate, and well-cited responses tailored to enterprise needs.
```

### Special Requirements/Limitations
- **Prompt Template:** Grounded generation requires specific prompt template; deviating reduces performance
- **Training:** Mixture of supervised fine-tuning and preference fine-tuning
- **RAG Configuration:** Takes conversation + optional preamble + list of document snippets
- **Grounding/Citations:** Trained to include citations in responses
- **Tool Use:** Only needs function name, definition (Python), and argument schema
- **Integration:** Works best with Cohere's Embed and Rerank models
- **Languages:** English, French, Spanish, Italian, German, Brazilian Portuguese, Japanese, Korean, Simplified Chinese, Arabic
- **Size:** 35B parameters (scalable category)

### Benchmark Scores
- Highly competitive RAG performance
- Strong tool-use capabilities
- Optimized for production-scale enterprise use

---

## 10. WizardLM 2 8x22B

### System Prompt Support
**YES** - Fully supported
- Uses Vicuna prompt format
- **CRITICAL:** "Please use the same system prompts strictly with us to guarantee the generation quality."

### Reasoning Effort Parameter
**NONE** - Does not support reasoning effort levels

### Supported Parameters
| Parameter | Support | Range/Values | Notes |
|-----------|---------|--------------|-------|
| `temperature` | ✅ Yes | 0.0-2.0 | Supported |
| `top_p` | ✅ Yes | 0.0-1.0 | Supported |
| `top_k` | ✅ Yes | 1-100+ | Supported |
| `frequency_penalty` | ✅ Yes | -2.0 to 2.0 | Supported |
| `presence_penalty` | ✅ Yes | -2.0 to 2.0 | Supported |
| `max_tokens` | ✅ Yes | 1-64000 | Context-dependent |

### Context Window
**32,000-64,000 tokens** (varies by quantization)

### Optimal Use Case
**Complex Chat, Multilingual, Reasoning, and Agent Tasks**
- Advanced conversational AI
- Multilingual communication
- Complex reasoning tasks
- Agent-based interactions
- Writing and content creation
- Coding assistance
- Mathematical problem-solving
- Virtual assistants and educational tutors
- Interactive training systems

### Recommended System Prompt
**Required Vicuna Format:**
```
A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.
```

**Note:** Model documentation emphasizes using this exact format for guaranteed quality.

### Special Requirements/Limitations
- **Architecture:** Built on Mixtral-8x22B-v0.1 base (MoE architecture)
- **Total Parameters:** 141B
- **MoE Configuration:** 8 experts, choose 2
- **Training:** Fully AI-powered synthetic training system
- **Prompt Format:** MUST use Vicuna format for optimal quality
- **Multi-turn:** Supports multi-turn conversations
- **Comparison:** Slightly below GPT-4-1106-preview, stronger than Command R Plus and GPT-4-0314
- **vs Mixtral 8x22B:** Enhanced performance from WizardLM fine-tuning

### Benchmark Scores
- **MT-Bench:** Highly competitive with GPT-4-Turbo and Claude-3
- **IFEval:** 52.72% accuracy
- **BBH (3-Shot):** 48.58%
- Strong performance on writing, coding, math, reasoning, agent, and multilingual tasks

---

## 11. DBRX Instruct

### System Prompt Support
**YES** - Fully supported

### Reasoning Effort Parameter
**NONE** - Does not support reasoning effort levels

### Supported Parameters
| Parameter | Support | Range/Values | Notes |
|-----------|---------|--------------|-------|
| `temperature` | ✅ Yes | 0.0-2.0 | Supported |
| `top_p` | ✅ Yes | 0.0-1.0 | Supported |
| `top_k` | ✅ Yes | 1-100+ | Supported |
| `frequency_penalty` | ⚠️ Limited | - | Framework-dependent |
| `presence_penalty` | ⚠️ Limited | - | Framework-dependent |
| `max_tokens` | ✅ Yes | 1-32768 | Context window limit |

### Context Window
**32,768 tokens** (32K)

### Optimal Use Case
**Enterprise Applications: Code, SQL, and RAG**
- Code generation and programming
- SQL query generation and database tasks
- Retrieval-augmented generation (RAG)
- General language understanding
- Mathematical problem-solving
- Enterprise-focused applications

### Recommended System Prompt
```
You are DBRX, a state-of-the-art open language model developed by Databricks with a fine-grained mixture-of-experts architecture. You excel at:
- Generating high-quality code across multiple programming languages
- Creating accurate SQL queries and database solutions
- Retrieval-augmented generation tasks
- Mathematical reasoning and problem-solving
- Enterprise-level language understanding

Provide clear, accurate, and practical solutions optimized for production use.
```

### Special Requirements/Limitations
- **MoE Architecture:** 132B total parameters, 36B active per input
- **Experts:** 16 experts, activates 4 (vs Mixtral/Grok-1: 8 experts, activates 2)
- **Expert Combinations:** 65x more possible combinations than Mixtral/Grok-1
- **Training Data:** 12T tokens of curated data
- **Tokenizer:** Converted GPT-4 tokenizer (tiktoken)
- **Architecture Components:**
  - Rotary position encodings (RoPE)
  - Gated linear units (GLU)
  - Grouped query attention (GQA)
- **Hardware:** Requires ~264GB RAM
- **Inference Speed:** 2-3x higher throughput than 132B non-MoE models
- **Batch Scaling:** 2x speed of dense 70B models at 32+ concurrent users
- **Deployment:** Available via Databricks Foundation Model APIs (pay-per-token and provisioned throughput)
- **Frameworks:** vLLM, TensorRT-LLM, MLX (Apple M-series), llama.cpp

### Benchmark Scores
- **HumanEval:** 70.1% (vs Mixtral Base: 40.2%)
- **GSM8k:** 66.9% (vs Mixtral Base: 57.6%)
- **MMLU:** 73.7% (vs Mixtral Instruct: 71.4%)
- **Hugging Face Open LLM Leaderboard:** 74.5% (highest at release)
- **RAG Performance:** Leading among open models and GPT-3.5 Turbo

---

## Quick Comparison Table

| Model | Size | System Prompt | Context | Reasoning Effort | Best For | Key Limitation |
|-------|------|--------------|---------|------------------|----------|----------------|
| **Qwen 2.5 Coder 32B** | 32B | ✅ Yes | 128K | ❌ None | Code generation, multi-lang dev | Temp must be ≥0.6 |
| **DeepSeek Coder V2 Lite** | 16B (2.4B active) | ✅ Yes | 128K | ❌ None | Efficient coding, 338 languages | MoE architecture |
| **Gemma 2 27B** | 27B | ❌ No | 8K | ❌ None | General text, reasoning | No system prompt support |
| **Llama 3.1 70B** | 70B | ✅ Yes | 128K | ❌ None | Dialogue, tool calling | Response may cap at 4K |
| **Llama 3.3 70B** | 70B | ✅ Yes | 128K+ | ❌ None | Enhanced 3.1 with latest techniques | Newer model, less documentation |
| **Mistral Large 2 123B** | 123B | ✅ Yes | 128K | ❌ None | Advanced reasoning, code, multilingual | Requires 300GB+ GPU (or quantized) |
| **Nemotron 70B** | 70B | ✅ Yes | 128K | ❌ None | Helpfulness-optimized chat | Not for specialized domains (math) |
| **QwQ 32B** | 32B | ✅ Yes | 128K | ⚠️ Thinking Mode | Reasoning with visible process | Must use temp=0.6, topP=0.95 |
| **Command R 35B** | 35B | ✅ Yes | 128K | ❌ None | RAG, tool calling, enterprise | Specific prompt template required |
| **WizardLM 2 8x22B** | 141B (8x22B MoE) | ✅ Yes | 32K-64K | ❌ None | Complex chat, multilingual, agents | Must use Vicuna prompt format |
| **DBRX Instruct** | 132B (36B active) | ✅ Yes | 32K | ❌ None | Code, SQL, RAG for enterprise | Requires 264GB RAM |

---

## Parameter Support Legend

- ✅ **Yes:** Fully supported and documented
- ⚠️ **Limited:** Support varies by framework or limited documentation
- ❌ **None:** Not supported or not applicable

---

## Reasoning Effort Notes

Only OpenAI's o1, o3, and o3-mini models currently support the `reasoning_effort` parameter (low/medium/high). The QwQ 32B model implements a different approach with visible thinking via `<think>` tags rather than a controllable effort parameter.

---

## Sources & References

This guide is compiled from official documentation and research:

- [Qwen 2.5 Coder Documentation](https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct)
- [DeepSeek Coder V2 GitHub](https://github.com/deepseek-ai/DeepSeek-Coder-V2)
- [Gemma Documentation](https://ai.google.dev/gemma/docs/core/prompt-structure)
- [Meta Llama Documentation](https://www.llama.com/docs/model-cards-and-prompt-formats/)
- [Mistral AI Documentation](https://mistral.ai/news/mistral-large-2407)
- [NVIDIA Nemotron](https://huggingface.co/nvidia/Llama-3.1-Nemotron-70B-Instruct)
- [QwQ Blog](https://qwenlm.github.io/blog/qwq-32b/)
- [Cohere Command R](https://docs.cohere.com/docs/command-r)
- [WizardLM 2](https://wizardlm.github.io/WizardLM2/)
- [Databricks DBRX](https://www.databricks.com/blog/introducing-dbrx-new-state-art-open-llm)

---

**Document Version:** 1.0
**Created:** December 2024
**Maintained for:** RTX 3090 AI Router Project
