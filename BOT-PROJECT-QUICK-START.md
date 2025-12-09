# 🤖 Bot & Project Management System - Quick Start

## 📖 Overview

This guide shows you how to create bots and projects with custom configurations for your RTX 3090 models.

## 📁 Directory Structure

```
D:\models\
├── projects/              # Your project configurations
│   ├── coding-assistant/
│   │   ├── config.json   # Project configuration
│   │   ├── system-prompt.txt
│   │   └── chat-history.json
│   ├── research-helper/
│   └── creative-writer/
├── bots/                  # Reusable bot configurations
│   ├── qwen3-coder-default.json
│   ├── phi4-reasoning.json
│   └── gemma3-creative.json
└── config-templates.json # All available parameters
```

## 🚀 Creating a New Project

### 📂 Step 1: Create Project Directory

```bash
mkdir -p D:\models\projects\my-coding-project
cd D:\models\projects\my-coding-project
```

### ⚙️ Step 2: Create config.json

```json
{
  "project_name": "my-coding-project",
  "description": "Personal coding assistant",
  "model": "qwen3-coder-30b",
  "created": "2025-12-08",

  "configuration": {
    "model_path": "/mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
    "ngl": 999,
    "threads": 24,
    "batch_size": 512,
    "ubatch_size": 512,
    "flash_attention": true,
    "cache_type_k": "q8_0",
    "cache_type_v": "q8_0",
    "no_ppl": true,
    "mlock": true,

    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 20,
    "min_p": 0.05,
    "repeat_penalty": 1.5,

    "context_size": 32768,
    "max_tokens": 4096,

    "jinja": true
  },

  "system_prompt_file": "system-prompt.txt",

  "metadata": {
    "use_case": "coding",
    "language": "Python, JavaScript, Rust",
    "expertise_level": "senior"
  }
}
```

### 📝 Step 3: Create system-prompt.txt

```
You are an expert software engineer specializing in Python, JavaScript, and Rust.

Your responses should:
- Write clean, well-documented code
- Follow best practices and design patterns
- Include error handling
- Provide clear explanations
- Consider performance and security

Code style preferences:
- Python: PEP 8, type hints
- JavaScript: ES6+, async/await
- Rust: Idiomatic Rust, proper ownership

Always explain your reasoning and suggest improvements.
```

## 🎨 Pre-Made Bot Templates

### Qwen3 Coder Bot

**File**: `bots/qwen3-coder-default.json`

```json
{
  "bot_name": "Qwen3 Coder Default",
  "model_id": "qwen3-coder-30b",
  "config": {
    "model_path": "/mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 20,
    "jinja": true,
    "ngl": 999,
    "threads": 24
  },
  "system_prompt": "You are an expert programmer. Write clean, efficient code with clear explanations."
}
```

### Phi-4 Reasoning Bot

**File**: `bots/phi4-reasoning.json`

```json
{
  "bot_name": "Phi-4 Reasoning",
  "model_id": "phi4-14b",
  "config": {
    "model_path": "/mnt/d/models/organized/Phi-4-reasoning-plus-Q6_K.gguf",
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "jinja": true,
    "ngl": 999,
    "threads": 24
  },
  "system_prompt": "You are an expert at logical reasoning and problem-solving. Break down complex problems systematically.",
  "notes": "DO NOT use 'think step-by-step' prompts - reasoning is built-in"
}
```

### Gemma-3 Creative Bot

**File**: `bots/gemma3-creative.json`

```json
{
  "bot_name": "Gemma-3 Creative Writer",
  "model_id": "gemma3-27b",
  "config": {
    "model_path": "/mnt/d/models/organized/Gemma-3-27B-Instruct-Abliterated-IQ2_M.gguf",
    "temperature": 1.2,
    "min_p": 0.08,
    "top_p": 0.9,
    "mirostat": 2,
    "mirostat_tau": 5.0,
    "ngl": 999,
    "threads": 24
  },
  "system_prompt": null,
  "notes": "NO system prompt support. Use high temperature for creativity."
}
```

## ▶️ Running a Project

### Method 1: Manual Command

```bash
# Navigate to project
cd D:\models\projects\my-coding-project

# Read config
$config = Get-Content config.json | ConvertFrom-Json

# Build command
wsl bash -c "~/llama.cpp/build/bin/llama-cli \
  -m $($config.configuration.model_path) \
  --system-prompt '$(Get-Content system-prompt.txt)' \
  -p 'Write a Python function to sort a list' \
  -ngl $($config.configuration.ngl) \
  -t $($config.configuration.threads) \
  -b $($config.configuration.batch_size) \
  --temp $($config.configuration.temperature) \
  --top-p $($config.configuration.top_p) \
  --top-k $($config.configuration.top_k) \
  --jinja \
  --flash-attn \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --no-ppl \
  --mlock"
```

### Method 2: Simple Project Runner Script

Create `run-project.ps1`:

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectName,

    [Parameter(Mandatory=$true)]
    [string]$Prompt
)

$projectPath = "D:\models\projects\$ProjectName"
$configFile = "$projectPath\config.json"
$promptFile = "$projectPath\system-prompt.txt"

if (-not (Test-Path $configFile)) {
    Write-Host "Project not found: $ProjectName" -ForegroundColor Red
    exit 1
}

$config = Get-Content $configFile | ConvertFrom-Json
$systemPrompt = Get-Content $promptFile -Raw

# Build command
$cmd = @"
wsl bash -c "~/llama.cpp/build/bin/llama-cli \
  -m '$($config.configuration.model_path)' \
  --system-prompt '$systemPrompt' \
  -p '$Prompt' \
  -ngl $($config.configuration.ngl) \
  -t $($config.configuration.threads) \
  -b $($config.configuration.batch_size) \
  -ub $($config.configuration.ubatch_size) \
  -fa 1 \
  --cache-type-k $($config.configuration.cache_type_k) \
  --cache-type-v $($config.configuration.cache_type_v) \
  --no-ppl \
  --temp $($config.configuration.temperature) \
  --top-p $($config.configuration.top_p) \
  --top-k $($config.configuration.top_k) \
  -c $($config.configuration.context_size) \
  -n $($config.configuration.max_tokens) \
  --jinja \
  --mlock"
"@

Invoke-Expression $cmd
```

**Usage**:
```powershell
.\run-project.ps1 -ProjectName "my-coding-project" -Prompt "Write a Python function to sort a list"
```

## 📚 Configuration Reference

See `config-templates.json` for complete list of all 50+ available parameters including:

### Core Parameters
- `ngl`, `threads`, `batch_size`, `ubatch_size`

### Sampling Parameters
- `temperature`, `top_p`, `top_k`, `min_p`
- `repeat_penalty`, `presence_penalty`, `frequency_penalty`
- `mirostat`, `mirostat_tau`, `mirostat_eta`

### Context Parameters
- `context_size`, `max_tokens`
- `cache_type_k`, `cache_type_v`

### Performance Parameters
- `flash_attention`, `no_ppl`, `mlock`, `mmap`, `numa`

### Model-Specific Flags
- `jinja`, `rope_freq_base`, `rope_freq_scale`

### Advanced Parameters
- `seed`, `grammar`, `json_schema`, `stop_sequences`, `logit_bias`

## 💡 Quick Project Examples

### 1. Python Coding Assistant

```json
{
  "project_name": "python-dev",
  "model": "qwen3-coder-30b",
  "configuration": {
    "temperature": 0.4,
    "top_p": 0.95,
    "jinja": true
  },
  "system_prompt": "Expert Python developer. Write Pythonic code with type hints and docstrings."
}
```

### 2. Math Tutor

```json
{
  "project_name": "math-tutor",
  "model": "phi4-14b",
  "configuration": {
    "temperature": 0.7,
    "jinja": true
  },
  "system_prompt": "Patient math tutor. Explain concepts clearly with step-by-step solutions."
}
```

### 3. Creative Writing Partner

```json
{
  "project_name": "story-writer",
  "model": "gemma3-27b",
  "configuration": {
    "temperature": 1.2,
    "min_p": 0.08,
    "mirostat": 2
  },
  "system_prompt": null
}
```

## 🌐 Opening Models to Other Agents

### Method 1: llama.cpp Server Mode

```bash
# Start server
wsl bash -c "~/llama.cpp/build/bin/llama-server \
  -m /mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf \
  -ngl 999 \
  -fa 1 \
  --ctx-size 32768 \
  --parallel 4 \
  --cont-batching \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --port 8080"

# Other agents can connect to http://localhost:8080
```

### Method 2: OpenAI-Compatible API

Use llama-server with OpenAI-compatible endpoint:

```bash
# Start server with OpenAI API
wsl bash -c "~/llama.cpp/build/bin/llama-server \
  -m /mnt/d/models/organized/model.gguf \
  -ngl 999 \
  --port 8080 \
  --api-key your-api-key"

# Agents connect via OpenAI SDK
```

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="your-api-key"
)

response = client.chat.completions.create(
    model="local-model",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello!"}
    ]
)
```

## ✅ Next Steps

1. Create your first project using the templates above
2. Experiment with different configurations
3. Use the evaluation framework to test different settings
4. Build automation scripts for your workflows

---

**All configuration parameters are documented in `config-templates.json`!**
