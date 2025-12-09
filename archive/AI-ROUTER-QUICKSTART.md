# AI Router - Quick Start Guide

## Overview

The AI Router is an intelligent command-line application that automatically selects and executes the optimal LLM model based on your use case. It features a colorful terminal interface and seamless model switching.

## Features

- **Automatic Model Selection**: Detects use case from your prompt and recommends the best model
- **Manual Model Selection**: Browse and manually select from available models
- **Colorful Terminal UI**: Beautiful, easy-to-read interface with ANSI colors
- **Platform Aware**: Automatically adapts for RTX 3090 (WSL) or MacBook M4 (MLX)
- **2025 Research Optimized**: Uses latest optimal parameters from Sep-Nov 2025 research
- **System Prompt Integration**: Automatically loads model-specific system prompts
- **Interactive Help**: Built-in guides for parameters and system prompts

## Installation

### Requirements

**For Windows/WSL (RTX 3090/4060 Ti):**
- Python 3.8+
- WSL2 with llama.cpp installed
- CUDA toolkit

**For macOS (M4 Pro):**
- Python 3.8+
- MLX framework installed

### Setup

```bash
# Make executable (optional)
chmod +x ai-router.py

# Or run with Python
python3 ai-router.py
```

## Usage

### Interactive Mode (Recommended)

```bash
python ai-router.py
```

This launches the interactive menu with options:

1. **Auto-select model** - Enter a prompt, AI Router detects use case and recommends model
2. **Manually select model** - Browse all models and choose one
3. **List all models** - View complete model catalog
4. **View system prompts** - Learn about system prompt customization
5. **View parameters guide** - See optimal parameters for 2025
6. **Exit**

### Command-Line Options

```bash
# List all available models
python ai-router.py --list

# Show help
python ai-router.py --help
```

## Use Case Detection

AI Router automatically detects your use case and selects the optimal model:

| Use Case | Keywords | Recommended Models |
|----------|----------|-------------------|
| **Coding** | code, function, debug, python, javascript | Qwen3 Coder 30B, Qwen2.5 Coder 32B |
| **Reasoning** | calculate, prove, math, logic, analyze | Phi-4 14B, Ministral-3 14B |
| **Creative** | story, poem, creative, write, fiction | Gemma 3 27B |
| **Research** | research, explain, summary, analyze | Qwen3 14B, Qwen2.5 14B |
| **General** | Everything else | Qwen2.5 14B, Qwen3 14B |

## Example Workflow

### Auto-Select Example

```
$ python ai-router.py

[Interactive menu appears]
> Select option: 1

Enter your prompt: Write a Python function to calculate Fibonacci numbers

Detected use case: CODING
Recommended model: Qwen3 Coder 30B Q4_K_M

[Model info displayed]

Run this model? [Y/n]: y

[Model executes with optimal parameters]
```

### Manual Select Example

```
$ python ai-router.py

[Interactive menu appears]
> Select option: 2

[Models list displayed]
> Select model number: 3

[Phi-4 14B info displayed]

Enter your prompt: Prove that the square root of 2 is irrational

[Model executes]
```

## Platform-Specific Information

### RTX 3090 / 4060 Ti (WSL)

**Optimal Parameters (2025):**
- `-ngl 999` - Full GPU offload
- `-t 24` - All CPU threads
- `-b 512` - Minimum batch size
- `-fa 1` - Flash Attention
- `--cache-type-k q8_0` - KV cache quantization
- `--no-ppl` - Skip perplexity (+15% speedup)

**Available Models:**
- Qwen3 Coder 30B Q4_K_M (18GB) - 25-35 tok/sec
- Qwen2.5 Coder 32B Q4_K_M (19GB) - 25-35 tok/sec
- Phi-4 14B Q6_K (12GB) - 35-55 tok/sec
- Gemma 3 27B IQ2_M (12GB) - 25-40 tok/sec
- Ministral-3 14B Q5_K_M (10GB) - 35-50 tok/sec

### MacBook M4 Pro (MLX)

**Framework:** MLX (2-3x faster than llama.cpp on Mac)

**Available Models:**
- Qwen2.5 14B Q5_K_M (11GB) - 50-70 tok/sec
- Qwen2.5 Coder 14B Q4_K_M (8GB) - 50-75 tok/sec
- Phi-4 14B Q6_K (12GB) - 60-75 tok/sec
- Gemma-3 9B Q6_K (8GB) - 85-110 tok/sec

## System Prompts

System prompts are automatically loaded from:
- **Windows/WSL**: `D:\models\system-prompt-<model-id>.txt`
- **macOS**: `~/models/system-prompt-<model-id>.txt`

You can customize these files to change model behavior.

## Critical Notes (2025 Research)

**DO:**
- ✓ Use WSL for RTX GPUs (within 1% of native Linux)
- ✓ Use MLX for M4 Mac (2-3x faster than llama.cpp)
- ✓ Use temperature >= 0.6 for Qwen models
- ✓ Use --jinja flag for Phi-4 and Qwen3

**DON'T:**
- ✗ Use temp 0 with Qwen (causes endless loops)
- ✗ Use "think step-by-step" with reasoning models (degrades performance)
- ✗ Skip Flash Attention on CUDA GPUs (miss 1.2x speedup)
- ✗ Run native Windows llama.cpp (WSL is faster)

## Troubleshooting

### Model Not Found

**Issue:** Path error when trying to run model

**Solution:**
1. Check model paths in `ai-router.py`
2. Update paths to match your installation
3. Ensure models are downloaded

### WSL Command Fails

**Issue:** WSL command not recognized

**Solution:**
1. Ensure WSL2 is installed
2. Verify llama.cpp is built in `~/llama.cpp/build/bin/`
3. Check CUDA drivers

### MLX Not Found (macOS)

**Issue:** MLX framework not installed

**Solution:**
```bash
python3 -m venv ~/mlx_venv
source ~/mlx_venv/bin/activate
pip install mlx mlx-lm huggingface_hub
```

## Customization

### Adding New Models

Edit `ai-router.py` and add to the appropriate model dictionary:

```python
"model-id": {
    "name": "Model Name",
    "path": "/path/to/model.gguf",
    "size": "10GB",
    "speed": "30-40 tok/sec",
    "use_case": "Description",
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "context": 32768,
    "special_flags": [],
    "system_prompt": "system-prompt-file.txt",
    "notes": "Special notes",
    "framework": "llama.cpp"  # or "mlx"
}
```

### Modifying Use Case Detection

Edit the `detect_use_case()` method in `ModelDatabase` class to add keywords or use cases.

## Performance Expectations

### RTX 3090 (24GB VRAM)

| Model Size | Quantization | Speed | Use Case |
|-----------|--------------|-------|----------|
| 14B | Q6_K | 35-55 tok/sec | Daily use |
| 30-32B | Q4_K_M | 25-35 tok/sec | Heavy tasks |
| 70B | IQ2_M | 15-25 tok/sec | Maximum capability |

### M4 Pro (24GB Unified)

| Model Size | Quantization | Speed | Use Case |
|-----------|--------------|-------|----------|
| 9B | Q6_K | 85-110 tok/sec | Speed champion |
| 14B | Q5_K_M | 50-75 tok/sec | Best balance |
| 70B | IQ2_M | 15-22 tok/sec | Max quality (slow) |

## Links and Resources

- **Research Summary**: `D:\models\2025-RESEARCH-SUMMARY.md`
- **Optimal Parameters**: `D:\models\LLAMA-CPP-OPTIMAL-PARAMS.lock`
- **M4 Guide**: `D:\models\MACBOOK-M4-OPTIMIZATION-GUIDE.md`
- **System Prompts**: `D:\models\system-prompt-*.txt`

## Version

**Version**: 1.0
**Last Updated**: 2025-12-08
**Research Period**: September-November 2025

---

**Enjoy intelligent model routing!**
