# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is a **local LLM models repository** optimized for RTX 3090 24GB and RTX 4060 Ti 16GB GPUs. It contains 10 production-ready models with research-optimized system prompts, execution scripts, and a Python-based AI Router for intelligent model selection.

**Primary Goal**: Run state-of-the-art local LLMs with maximum performance using llama.cpp in WSL with CUDA acceleration.

## Critical Architecture Concepts

### 1. WSL-First Execution Strategy
- **NEVER use Windows executables** for llama.cpp - WSL provides 45-60% better performance
- **ALWAYS run models through WSL**: `wsl bash -c "~/llama.cpp/build/bin/llama-cli ..."`
- llama.cpp location in WSL: `~/llama.cpp/build/bin/llama-cli`
- Model files are accessible in WSL at `/mnt/d/models/`
- WSL provides within 1% of native Linux performance for GPU workloads

### 2. Model Organization
- **Production models**: `D:\models\organized\` - 9 models totaling ~99GB
- **Secondary models**: `D:\models\rtx4060ti-16gb\` - 5 smaller models for 16GB GPU
- **System prompts**: Co-located with models in same directories (e.g., `Qwen3-Coder-30B-SYSTEM-PROMPT.txt`)
- **GGUF format only** - quantized models optimized for consumer GPUs

### 3. AI Router Architecture (ai-router.py)
The AI Router is the **primary interface** for model execution:

**Core Components**:
- `ModelDatabase` class: Contains model metadata, optimal parameters, and use-case mappings
- `AIRouter` class: Interactive CLI with auto-selection, manual selection, and documentation viewing
- Platform detection: Automatically selects RTX 3090 models (WSL) or M4 models (MLX)
- Use-case detection: Analyzes prompts to recommend optimal models (coding, reasoning, creative, research)

**Key Features**:
- Auto-loads model-specific system prompts
- Enforces 2025-optimized parameters (Flash Attention, KV cache quantization)
- Beautiful ANSI-colored terminal UI
- Built-in documentation viewer

### 4. Optimal Parameter Lock System
Critical safeguards prevent performance degradation:

**Locked Parameters** (in `LLAMA-CPP-OPTIMAL-PARAMS.lock`):
- `-ngl 999` - Full GPU offload (Aug 2025+ llama.cpp default)
- `-t 24` - All CPU threads (Ryzen 9 5900X: 12 cores/24 threads)
- `-b 512` - Minimum batch size (2025 research finding)
- `-ub 512` - Logical batch for prompt processing
- `-fa 1` - Flash Attention (+20% speed, 50% memory reduction)
- `--cache-type-k q8_0` and `--cache-type-v q8_0` - KV cache quantization (50% memory savings)
- `--no-ppl` - Skip perplexity calculation (+15% speedup)
- `--mlock` - Lock model in RAM to prevent paging

**DO NOT modify these parameters** - they are research-validated for maximum performance.

### 5. Model-Specific Critical Requirements

#### Qwen Models (Qwen3, Qwen2.5):
- **NEVER use temperature 0.0** - causes infinite loops
- **ALWAYS use `--jinja` flag** for proper chat template handling
- **Minimum temperature: 0.6** (research-validated)
- Large context models need `--enable-chunked-prefill --max-num-batched-tokens 131072`

#### Phi-4:
- **ALWAYS use `--jinja` flag** - required for proper operation
- **DO NOT use "think step-by-step" prompts** - model has internal reasoning
- Optimal temperature: 0.7-0.8

#### DeepSeek-R1:
- **NO system prompt support** - performs worse with system prompts
- Use user prompt template only from system prompt file
- Built-in chain-of-thought reasoning

#### Gemma 3:
- **NO system prompt support** - use prompt framing template instead
- System prompt files contain user-facing templates, not system prompts
- Requires higher temperature (0.9-1.0) and min-p sampling

## Common Commands

### Running Models

#### Option 1: AI Router (Recommended)
```powershell
# Launch interactive AI Router
.\LAUNCH-AI-ROUTER.ps1

# Direct WSL launch
wsl bash -c "cd /mnt/d/models && ~/hf_venv/bin/python3 ai-router.py"

# Command-line options
wsl bash -c "cd /mnt/d/models && ~/hf_venv/bin/python3 ai-router.py --list"
wsl bash -c "cd /mnt/d/models && ~/hf_venv/bin/python3 ai-router.py --help"
```

#### Option 2: PowerShell Runner with System Prompts
```powershell
# Run model with automated system prompt loading
.\RUN-MODEL-WITH-PROMPT.ps1 -Model Qwen3Coder -UserPrompt "Write a Python function" -MaxTokens 512

# Available models:
# Llama70B, Qwen3Coder, DolphinVenice, Phi4, Gemma3,
# Ministral3, DeepSeekR1, WizardVicuna, Dolphin8B,
# Qwen14BInstruct, Qwen14BUncensored, Llama8B, QwenCoder7B
```

#### Option 3: Direct llama.cpp (Advanced)
```bash
# Example: Qwen3 Coder with all optimizations
wsl bash -c "~/llama.cpp/build/bin/llama-cli \
  -m /mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf \
  -p 'Your prompt here' \
  -ngl 999 \
  -t 24 \
  -b 512 \
  -ub 512 \
  -fa 1 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --no-ppl \
  --temp 0.7 \
  --top-p 0.8 \
  --top-k 20 \
  -c 32768 \
  --jinja \
  --mlock"
```

### Validation & Monitoring

```powershell
# Validate llama.cpp command for optimal parameters
.\VALIDATE-CONFIG.ps1

# Monitor model performance (tokens/sec)
.\MONITOR-PERFORMANCE.ps1 -ModelPath "/mnt/d/models/organized/model.gguf" -ExpectedMinToksPerSec 20

# Ensure WSL is being used (not Windows executables)
.\ENSURE-WSL-USAGE.ps1
```

### System Prompt Creation

```powershell
# Generate custom system prompt using Qwen3 Coder
.\CREATE-SYSTEM-PROMPTS.ps1 -Task "Create system prompt" -UseCase "Medical research analysis" -Model "Research assistant"

# Generate user prompt template
.\CREATE-SYSTEM-PROMPTS.ps1 -Task "Create user template" -Category "Code review" -Language "Python"

# Analyze existing prompt
.\CREATE-SYSTEM-PROMPTS.ps1 -Task "Analyze prompt" -PromptFile "D:\prompts\my-prompt.txt"
```

### Model Organization

```powershell
# Organize downloaded models (categorizes by size/use-case)
.\organize-models.ps1

# Run model in WSL (wrapper for optimal parameters)
.\run-in-wsl.ps1 -ModelPath "organized/model.gguf" -Prompt "Your prompt"

# Run model with custom prompt (simpler interface)
.\run-model.ps1 -ModelName "Qwen3Coder" -Prompt "Your prompt"
```

## Model Selection Guide

| Use Case | Primary Model | Alternative | Rationale |
|----------|---------------|-------------|-----------|
| **Coding** | Qwen3 Coder 30B | Qwen2.5 Coder 32B | 94% HumanEval, 256K context, agentic workflows |
| **Reasoning** | Phi-4 14B | Ministral-3 14B | 78% AIME 2025, best reasoning at size |
| **Math** | DeepSeek-R1 14B | Phi-4 14B | 94.3% MATH-500, chain-of-thought |
| **Research** | Llama 3.3 70B | Dolphin-Mistral 24B | 70B params, abliterated, deep analysis |
| **Creative Writing** | Gemma 3 27B | - | 128K context, prose quality, abliterated |
| **Uncensored** | Dolphin-Mistral 24B | Llama 3.3 70B | 2.2% refusal rate (lowest available) |
| **Fast/General** | Dolphin 3.0 8B | Wizard-Vicuna 13B | 60-90 tok/sec on RTX 3090 |

## Project Structure

```
D:\models\
├── ai-router.py                  # Main AI Router application
├── LAUNCH-AI-ROUTER.ps1          # WSL launcher for AI Router
├── RUN-MODEL-WITH-PROMPT.ps1     # Automated model runner
├── CREATE-SYSTEM-PROMPTS.ps1     # System prompt generator
├── VALIDATE-CONFIG.ps1           # Parameter validation
├── MONITOR-PERFORMANCE.ps1       # Performance monitoring
├── ENSURE-WSL-USAGE.ps1          # WSL enforcement checker
├── organize-models.ps1           # Model organization script
├── run-in-wsl.ps1               # WSL execution wrapper
├── run-model.ps1                # Simple model runner
├── model-registry.json          # Model metadata registry
├── config-templates.json        # 50+ parameter templates
├── LLAMA-CPP-OPTIMAL-PARAMS.lock # Locked optimal parameters
├── MODEL-PARAMETERS-QUICK-REFERENCE.json # Parameter quick ref
├── README.md                    # Complete project documentation
├── organized/                   # Production models (RTX 3090)
│   ├── *.gguf                  # Model files
│   └── *-SYSTEM-PROMPT.txt     # Model-specific system prompts
├── rtx4060ti-16gb/             # Secondary models (16GB GPU)
│   ├── qwen25-14b-instruct/
│   ├── qwen25-14b-uncensored/
│   ├── llama31-8b-instruct/
│   └── qwen25-coder-7b/
├── gguf/                       # Model download staging area
└── archive/                    # Old/deprecated models
```

## Important Files

### Documentation
- `README.md` - Comprehensive guide (1,195 lines): models, benchmarks, prompts, parameters
- `HOW-TO-RUN-AI-ROUTER.md` - AI Router usage guide
- `BOT-PROJECT-QUICK-START.md` - Bot/project creation
- `SYSTEM-PROMPTS-QUICK-START.md` - System prompt usage
- `COMPREHENSIVE-EVALUATION-FRAMEWORK-PROMPT.md` - Model evaluation
- `2025-RESEARCH-SUMMARY.md` - Latest research findings
- `MACBOOK-M4-OPTIMIZATION-GUIDE.md` - M4 Mac optimization

### Configuration
- `model-registry.json` - Model inventory and metadata
- `config-templates.json` - 50+ parameter configurations
- `LLAMA-CPP-OPTIMAL-PARAMS.lock` - Performance-critical locked params
- `MODEL-PARAMETERS-QUICK-REFERENCE.json` - Quick parameter reference

### Research & Analysis
- `2025-MODEL-UPGRADES-ANALYSIS.txt` - Model upgrade research
- `OPTIMIZED-SYSTEM-PROMPTS-2025-RESEARCH-BASED.txt` - System prompt research
- `OPTIMIZATION-STATUS-REPORT.txt` - Performance optimization status
- `FINAL-SETUP-REPORT-2025-12-08.txt` - Complete setup documentation

## Development Workflow

### Testing Models
1. Use AI Router for interactive testing: `.\LAUNCH-AI-ROUTER.ps1`
2. Auto-select uses prompt analysis to recommend optimal model
3. View model info before execution to verify parameters
4. Monitor tokens/sec during generation (should be 20+ for most models)

### Adding New Models
1. Download GGUF file to `D:\models\gguf\`
2. Move to appropriate directory (`organized\` or `rtx4060ti-16gb\`)
3. Create system prompt file: `[MODEL-NAME]-SYSTEM-PROMPT.txt`
4. Add entry to `ai-router.py` ModelDatabase:
   ```python
   "model-id": {
       "name": "Display Name",
       "path": "/mnt/d/models/organized/model.gguf",
       "size": "XGB",
       "speed": "XX-YY tok/sec",
       "use_case": "Primary use case",
       "temperature": 0.7,
       "top_p": 0.9,
       "top_k": 40,
       "context": 32768,
       "special_flags": [],  # e.g., ["--jinja"]
       "system_prompt": "system-prompt-file.txt",
       "notes": "Critical requirements",
       "framework": "llama.cpp"
   }
   ```
5. Add entry to `model-registry.json` for inventory tracking
6. Test with validation: `.\MONITOR-PERFORMANCE.ps1 -ModelPath "/mnt/d/models/organized/model.gguf"`

### Creating System Prompts
1. Research model's training data and capabilities
2. Review existing prompts in `organized/` for patterns
3. Use `CREATE-SYSTEM-PROMPTS.ps1` with Qwen3 Coder for generation
4. Test with representative prompts
5. Document special requirements in model notes

### Performance Optimization
1. **NEVER modify locked parameters** in LLAMA-CPP-OPTIMAL-PARAMS.lock
2. Test parameter changes one at a time
3. Benchmark with `MONITOR-PERFORMANCE.ps1`
4. Compare tokens/sec against expected ranges (see README.md benchmarks)
5. Validate with `VALIDATE-CONFIG.ps1` before committing

## Critical Rules

### MUST DO
- ✓ Run models through WSL for 45-60% better performance
- ✓ Use AI Router or RUN-MODEL-WITH-PROMPT.ps1 for system prompt automation
- ✓ Verify `-ngl 999` (full GPU offload) for all executions
- ✓ Use `--jinja` flag for Qwen and Phi-4 models
- ✓ Test with `MONITOR-PERFORMANCE.ps1` after parameter changes
- ✓ Check README.md for model-specific temperature requirements

### MUST NOT DO
- ✗ Use Windows llama.cpp executables (45-60% slower)
- ✗ Use temperature 0.0 with Qwen models (causes loops)
- ✗ Omit `--jinja` flag for Qwen3 or Phi-4
- ✗ Use system prompts with DeepSeek-R1 or Gemma 3
- ✗ Use "think step-by-step" prompts with reasoning models
- ✗ Modify parameters in LLAMA-CPP-OPTIMAL-PARAMS.lock
- ✗ Run Ollama instead of llama.cpp (not optimized)

## Hardware Context

**Primary System**: RTX 3090 24GB VRAM
- CPU: AMD Ryzen 9 5900X (12 cores / 24 threads)
- RAM: Sufficient for mlock (models locked in RAM)
- OS: Windows 11 with WSL2 (CUDA passthrough enabled)
- llama.cpp built with CUDA support in WSL

**Secondary System**: RTX 4060 Ti 16GB VRAM
- Models in `rtx4060ti-16gb/` directory
- Smaller models optimized for 16GB constraint

## Version Control

- **Git repository**: Active (`.git` directory present)
- **Large files excluded**: *.gguf, *.safetensors (see .gitignore)
- **Tracked files**: Scripts, configs, documentation, system prompts
- **Model files NOT committed** - too large for GitHub (10-22GB each)

## External Tools

- **llama.cpp**: Primary inference engine (WSL: `~/llama.cpp/build/bin/llama-cli`)
- **Python venv**: `~/hf_venv/` (contains colorama, termcolor, rich)
- **CUDA**: GPU acceleration via WSL CUDA passthrough
- **PowerShell 7.5+**: Required for scripts

## Additional Context

This repository represents 6 months of research (June-December 2024) into optimal local LLM deployment. The system prompts, parameters, and model selections are based on academic papers, community benchmarks (HumanEval, AIME, MATH-500, SWE-bench), and extensive testing.

Key research sources documented in README.md:
- Over 100+ sources including academic papers, official docs, community resources
- SPRIG, Instruction Hierarchy, Min-P Sampling research
- Anthropic, OpenAI, Meta, Alibaba, Microsoft, Mistral documentation
- r/LocalLLaMA, HuggingFace, GitHub community findings

The locked parameters and model configurations should be treated as production-validated and modified only with careful benchmarking.
