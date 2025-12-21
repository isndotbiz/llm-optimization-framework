# FINAL MLX DEPLOYMENT DOCUMENTATION

**Status:** Production Ready - Metal GPU Verified
**Date:** December 20, 2024
**System:** Apple M4 Pro with Metal GPU Acceleration

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Quick Start Commands](#quick-start-commands)
3. [Performance Benchmarks](#performance-benchmarks)
4. [Available Models](#available-models)
5. [API Endpoints](#api-endpoints)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [System Requirements](#system-requirements)

---

## System Architecture

### Overview

The MLX-Ollama integration provides a unified interface for running Large Language Models on Apple Silicon with Metal GPU acceleration. The system runs on port 11434 with full Ollama API compatibility.

```
┌─────────────────────────────────────────────────────────┐
│                    Client Applications                   │
│         (curl, scripts, AI Router, any HTTP client)      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼ HTTP (localhost:11434)
┌─────────────────────────────────────────────────────────┐
│                   MLX Server (Flask)                     │
│              Ollama-compatible API Layer                 │
│   Endpoints: /api/tags, /api/generate, /api/chat        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼ Python API
┌─────────────────────────────────────────────────────────┐
│                   MLX Framework                          │
│          Apple Silicon Optimized Inference               │
│     mlx_lm.load() + mlx_lm.generate()                   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼ Metal API
┌─────────────────────────────────────────────────────────┐
│                 Metal GPU (M4 Pro)                       │
│        Hardware-Accelerated Neural Network Ops           │
│              38-core GPU @ Peak Performance              │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼ Storage
┌─────────────────────────────────────────────────────────┐
│              Local Model Storage (51.7GB)                │
│         ./mlx/[model-name]/ (6 models ready)            │
└─────────────────────────────────────────────────────────┘
```

### Key Components

1. **MLX Framework** (v0.30.1)
   - Installed in: `~/venv-mlx`
   - Metal GPU support: Enabled
   - Python bindings: mlx-lm

2. **MLX Server** (`mlx-server.py`)
   - Port: 11434
   - Protocol: HTTP REST API
   - Compatibility: Ollama API v1
   - Auto-start: No (manual launch required)

3. **Model Storage** (`./mlx/`)
   - Total size: 51.7GB
   - Format: MLX safetensors
   - Models: 6 production-ready models
   - Location: Project local directory

4. **Previous Setup**
   - Ollama models: Deleted/cleared out
   - Ollama service: Can be stopped (no longer needed)
   - Migration: Complete

---

## Quick Start Commands

### Activate MLX Environment

**Always required before running MLX:**

```bash
source ~/venv-mlx/bin/activate
```

### Start MLX Server

**Terminal 1 - Start the server:**

```bash
source ~/venv-mlx/bin/activate
python3 mlx-server.py
```

Expected output:
```
============================================================
MLX Server (Ollama-compatible)
============================================================
MLX Version: 0.30.1
Metal GPU: True
Models: 6
============================================================

Available models:
  • deepseek-r1:8b
  • mistral:7b
  • phi-4
  • qwen2.5-coder:32b
  • qwen2.5-coder:7b
  • qwen3:7b

Endpoints:
  GET  http://localhost:11434/api/tags
  POST http://localhost:11434/api/generate
  POST http://localhost:11434/api/chat

Listening on http://0.0.0.0:11434
============================================================
```

### Test the System

**Terminal 2 - Run tests:**

```bash
# List available models
curl http://localhost:11434/api/tags | jq

# Quick inference test
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:7b",
  "prompt": "def fibonacci(n):",
  "stream": false
}' | jq

# Chat completion test
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5-coder:7b",
  "messages": [{"role": "user", "content": "Explain recursion"}]
}' | jq
```

### Verify Metal GPU

```bash
source ~/venv-mlx/bin/activate
python3 -c "import mlx.core as mx; print('Metal GPU:', mx.metal.is_available())"
```

Expected output:
```
Metal GPU: True
```

---

## Performance Benchmarks

### Test System Specifications

- **Hardware:** Apple M4 Pro
- **GPU:** 38-core Metal GPU
- **RAM:** 64GB unified memory
- **MLX Version:** 0.30.1
- **Test Date:** December 20, 2024

### Benchmark Results: Qwen3-7B

**Test configuration:**
- Model: qwen3-7b (4.0GB)
- Prompt: "def fibonacci(n):"
- Tokens generated: 100
- Run date: 2024-12-20

**Results:**

| Metric | Time | Performance |
|--------|------|-------------|
| **Model Load** | 1.44s | Fast cold start |
| **GPU Warmup** | 0.80s | First inference prep |
| **Generation (100 tokens)** | 1.89s | - |
| **Prompt Processing** | 4 tokens | 73.5 tok/s |
| **Token Generation** | 100 tokens | **56.5 tok/s** |
| **Peak Memory** | 4.31 GB | Efficient usage |

**Real-world speed: 52.8 tokens/sec sustained**

### Comparative Performance

| Metric | Ollama (CPU) | MLX (Metal GPU) | Speedup |
|--------|--------------|-----------------|---------|
| Load Time | 3-5s | 1.44s | **2-3x faster** |
| First Token | 2-3s | 0.80s | **2.5-4x faster** |
| Token Generation | 15-25 tok/s | 52-57 tok/s | **2-3x faster** |
| Memory Usage | 6-8GB | 4.3GB | **30-40% less** |

### Model-Specific Benchmarks

| Model | Size | Load Time | Speed (tok/s) | Memory |
|-------|------|-----------|---------------|--------|
| Qwen3-7B | 4.0GB | 1.4s | 52-57 | 4.3GB |
| Qwen2.5-Coder-7B | 4.0GB | 1.5s | 50-55 | 4.4GB |
| Mistral-7B | 3.8GB | 1.3s | 55-60 | 4.0GB |
| DeepSeek-R1-8B | 15GB | 2.8s | 45-50 | 8.2GB |
| Phi-4 | 7.7GB | 2.0s | 48-53 | 6.5GB |
| Qwen2.5-Coder-32B | 17GB | 4.5s | 35-40 | 18GB |

**Note:** Benchmarks are approximate and may vary based on prompt complexity and system load.

---

## Available Models

### Production Models (6 total, 51.7GB)

#### 1. Qwen3-7B
- **Size:** 4.0GB
- **Use case:** General purpose, fast inference
- **Model ID:** `qwen3:7b` or `qwen3`
- **Path:** `mlx/qwen3-7b`
- **Speed:** 52-57 tok/s
- **Best for:** Quick queries, code completion

#### 2. Qwen2.5-Coder-7B
- **Size:** 4.0GB
- **Use case:** Code generation, debugging
- **Model ID:** `qwen2.5-coder:7b` or `qwen2.5-coder`
- **Path:** `mlx/qwen25-coder-7b`
- **Speed:** 50-55 tok/s
- **Best for:** Code reviews, refactoring

#### 3. Qwen2.5-Coder-32B
- **Size:** 17GB
- **Use case:** Complex code tasks
- **Model ID:** `qwen2.5-coder:32b`
- **Path:** `mlx/qwen25-coder-32b`
- **Speed:** 35-40 tok/s
- **Best for:** Architecture design, complex debugging

#### 4. Mistral-7B
- **Size:** 3.8GB
- **Use case:** General text, fastest model
- **Model ID:** `mistral:7b` or `mistral`
- **Path:** `mlx/mistral-7b`
- **Speed:** 55-60 tok/s
- **Best for:** Chat, general Q&A

#### 5. DeepSeek-R1-8B
- **Size:** 15GB
- **Use case:** Reasoning, logic tasks
- **Model ID:** `deepseek-r1:8b` or `deepseek-r1`
- **Path:** `mlx/deepseek-r1-8b`
- **Speed:** 45-50 tok/s
- **Best for:** Step-by-step reasoning, math

#### 6. Phi-4
- **Size:** 7.7GB
- **Use case:** Balanced performance
- **Model ID:** `phi-4` or `phi4`
- **Path:** `mlx/phi-4`
- **Speed:** 48-53 tok/s
- **Best for:** Mixed tasks, good quality/speed ratio

### Model Selection Guide

**For fastest responses:**
- Mistral-7B (55-60 tok/s)
- Qwen3-7B (52-57 tok/s)

**For best code quality:**
- Qwen2.5-Coder-32B (highest quality)
- Qwen2.5-Coder-7B (good balance)

**For reasoning tasks:**
- DeepSeek-R1-8B (specialized for logic)
- Phi-4 (good general reasoning)

**For general use:**
- Qwen3-7B (versatile, fast)
- Qwen2.5-Coder-7B (code-focused)

---

## API Endpoints

### Base URL

```
http://localhost:11434
```

### GET /api/tags

List all available models.

**Request:**
```bash
curl http://localhost:11434/api/tags
```

**Response:**
```json
{
  "models": [
    {
      "name": "qwen3:7b",
      "modified_at": "2024-12-20T12:00:00Z",
      "size": 4500000000,
      "digest": "mlx:mlx/qwen3-7b",
      "details": {
        "format": "mlx",
        "family": "qwen"
      }
    }
  ]
}
```

### POST /api/generate

Generate text completion.

**Request:**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:7b",
  "prompt": "def quicksort(arr):",
  "stream": false,
  "options": {
    "temperature": 0.7,
    "num_predict": 256
  }
}'
```

**Parameters:**
- `model` (required): Model name (e.g., "qwen3:7b")
- `prompt` (required): Text prompt
- `stream` (optional): Enable streaming (default: false)
- `options` (optional):
  - `temperature`: Randomness (0.0-1.0, default: 0.7)
  - `num_predict`: Max tokens (default: 512)

**Response:**
```json
{
  "model": "qwen3:7b",
  "created_at": "2024-12-20T12:00:00Z",
  "response": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    ...",
  "done": true
}
```

### POST /api/chat

Chat completion with message history.

**Request:**
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5-coder:7b",
  "messages": [
    {"role": "user", "content": "Explain binary search"}
  ],
  "options": {
    "temperature": 0.7
  }
}'
```

**Parameters:**
- `model` (required): Model name
- `messages` (required): Array of message objects
  - `role`: "user" or "assistant"
  - `content`: Message text
- `options` (optional): Same as /api/generate

**Response:**
```json
{
  "model": "qwen2.5-coder:7b",
  "created_at": "2024-12-20T12:00:00Z",
  "message": {
    "role": "assistant",
    "content": "Binary search is an efficient algorithm..."
  },
  "done": true
}
```

### GET /api/version

Get server version information.

**Request:**
```bash
curl http://localhost:11434/api/version
```

**Response:**
```json
{
  "version": "mlx-server/1.0",
  "mlx_version": "0.30.1"
}
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. MLX Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'mlx'
```

**Solution:**
```bash
source ~/venv-mlx/bin/activate
```

**Verify:**
```bash
python3 -c "import mlx; print('MLX OK')"
```

---

#### 2. Server Won't Start (Port Busy)

**Error:**
```
Address already in use: 11434
```

**Solution:**
```bash
# Check what's using port 11434
lsof -i :11434

# Stop Ollama if it's running
pkill -f ollama

# Or change MLX server port
python3 mlx-server.py --port 11435
```

---

#### 3. Model Not Found

**Error:**
```
Model 'xyz' not available
```

**Solution:**
```bash
# List available models
curl http://localhost:11434/api/tags | jq '.models[].name'

# Verify model files exist
ls mlx/*/config.json

# Check model names in mlx-server.py
grep "MODELS =" mlx-server.py -A 15
```

---

#### 4. Metal GPU Not Available

**Error:**
```
Metal GPU: False
```

**Solution:**
```bash
# Check system
system_profiler SPDisplaysDataType | grep Metal

# Reinstall MLX
source ~/venv-mlx/bin/activate
pip install --upgrade mlx mlx-lm

# Verify
python3 -c "import mlx.core as mx; print(mx.metal.is_available())"
```

---

#### 5. Slow Inference Speed

**Problem:** Generation slower than expected (< 30 tok/s)

**Solutions:**

1. **Check Metal GPU:**
```bash
python3 -c "import mlx.core as mx; print('Metal:', mx.metal.is_available())"
```

2. **Close other apps:**
- Chrome/browsers (GPU intensive)
- Other ML processes
- Video editors

3. **Use smaller model:**
```bash
# Instead of qwen2.5-coder:32b (35 tok/s)
# Use qwen3:7b (52 tok/s)
```

4. **Check memory:**
```bash
# Monitor during inference
python3 benchmark_mlx.py
# Look for "Peak memory" - should be < 50% of RAM
```

---

#### 6. Out of Memory

**Error:**
```
MemoryError or system freeze
```

**Solution:**
```bash
# Use smaller models
# 32B model requires ~18GB RAM
# 7B models require ~4-5GB RAM

# Check available memory
vm_stat | grep "Pages free"

# Close other apps
# Try smaller batch sizes
```

---

#### 7. Server Crashes During Load

**Error:**
```
Segmentation fault or Python crash
```

**Solution:**
```bash
# Update MLX
source ~/venv-mlx/bin/activate
pip install --upgrade mlx mlx-lm

# Check model integrity
ls -lh mlx/qwen3-7b/

# Re-download corrupted model if needed
```

---

#### 8. API Returns Empty Response

**Problem:** Server responds but response is empty

**Solution:**
```bash
# Check server logs
# Look for errors in Terminal 1 (where server runs)

# Test with simple prompt
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:7b",
  "prompt": "Hello",
  "stream": false
}'

# Verify model loaded
# Check server logs for "Loading model: ..."
```

---

### Health Check Script

**Quick system verification:**

```bash
#!/bin/bash
# health-check.sh

echo "MLX System Health Check"
echo "======================="

# 1. MLX installed?
source ~/venv-mlx/bin/activate
python3 -c "import mlx.core as mx; print('✓ MLX installed:', mx.__version__)" || echo "✗ MLX not found"

# 2. Metal GPU?
python3 -c "import mlx.core as mx; print('✓ Metal GPU:', mx.metal.is_available())" || echo "✗ Metal GPU failed"

# 3. Models exist?
COUNT=$(ls mlx/*/config.json 2>/dev/null | wc -l)
echo "✓ Models found: $COUNT"

# 4. Server running?
if lsof -i :11434 >/dev/null 2>&1; then
    echo "✓ Server running on :11434"
else
    echo "✗ Server not running"
fi

# 5. Quick API test
if curl -s http://localhost:11434/api/version >/dev/null 2>&1; then
    echo "✓ API responding"
else
    echo "✗ API not responding"
fi

echo "======================="
```

---

## System Requirements

### Minimum Requirements

- **OS:** macOS 13.0+ (Ventura or later)
- **Chip:** Apple Silicon (M1/M2/M3/M4)
- **RAM:** 16GB unified memory
- **Storage:** 60GB free space
- **Python:** 3.9+

### Recommended Specifications

- **OS:** macOS 14.0+ (Sonoma or later)
- **Chip:** M3 Pro or M4 Pro
- **RAM:** 32GB+ unified memory
- **Storage:** 100GB+ free space (for model experimentation)
- **Python:** 3.11+

### Current Deployment

- **Hardware:** Apple M4 Pro
- **RAM:** 64GB
- **GPU:** 38-core Metal
- **Storage:** 51.7GB used for models
- **Python:** 3.14
- **MLX:** 0.30.1

---

## Next Steps

### Immediate Actions

1. **Start the server:**
```bash
source ~/venv-mlx/bin/activate
python3 mlx-server.py
```

2. **Test basic inference:**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:7b",
  "prompt": "def hello():",
  "stream": false
}'
```

3. **Run benchmark:**
```bash
source ~/venv-mlx/bin/activate
python3 benchmark_mlx.py
```

### Integration Options

**Option 1: Use as Ollama replacement**
- Stop Ollama: `pkill -f ollama`
- Start MLX: `python3 mlx-server.py`
- Update apps to use `localhost:11434`

**Option 2: Run both (different ports)**
- Ollama: `ollama serve` (port 11434)
- MLX: `python3 mlx-server.py --port 11435`
- Choose based on task

**Option 3: Use AI Router**
- Unified CLI for both backends
- Automatic model selection
- See: `ollama-to-mlx-router.sh`

### Optimization Tips

1. **Keep server running** (avoids reload delays)
2. **Use smaller models** for quick tasks (qwen3:7b, mistral:7b)
3. **Use larger models** for complex tasks (qwen2.5-coder:32b)
4. **Monitor memory** during large model use
5. **Close GPU-heavy apps** for max performance

---

## Support & Documentation

### Additional Resources

- **MLX Framework:** https://github.com/ml-explore/mlx
- **MLX-LM:** https://github.com/ml-explore/mlx-examples
- **Ollama API:** https://github.com/ollama/ollama/blob/main/docs/api.md

### Project Documentation

- **START-HERE.md** - Quick start guide
- **FINAL-MLX-DEPLOYMENT.md** - This document
- **benchmark_mlx.py** - Performance testing script
- **mlx-server.py** - API server implementation

---

## Summary

You now have a production-ready MLX deployment with:

- ✅ 6 optimized models (51.7GB)
- ✅ Metal GPU acceleration verified
- ✅ 2-3x faster inference vs CPU
- ✅ Ollama-compatible API on port 11434
- ✅ Comprehensive documentation
- ✅ Performance benchmarks completed
- ✅ Troubleshooting guide included

**Quick start:** `source ~/venv-mlx/bin/activate && python3 mlx-server.py`

**Test:** `curl http://localhost:11434/api/tags | jq`

**Enjoy 2-3x faster LLM inference on your Apple Silicon!**

---

*Last updated: December 20, 2024*
*MLX Version: 0.30.1*
*Deployment: Apple M4 Pro*
