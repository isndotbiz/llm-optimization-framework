# Multi-Machine Setup Guide

This document describes how to manage the AI Router system across three different computers with different hardware configurations.

## Machine Registry

| Machine | CPU | GPU | System RAM | VRAM | Location | Primary Use |
|---------|-----|-----|-----------|------|----------|-------------|
| **M4 MacBook Pro** | M4 (12-core CPU, 16-core GPU) | Apple GPU | 24GB unified | Integrated | `configs/m4-macbook-pro/` | Development, Portability |
| **Ryzen 3900X + 3090** | Ryzen 3900X (12-core, 24-thread) | RTX 3090 | 64GB DDR4 | 24GB | `configs/ryzen-3900x-3090/` | **PRIMARY** Production |
| **Xeon E5 + 4060 Ti** | Xeon E5-2676v3 (12-core, 24-thread) | RTX 4060 Ti | 96GB DDR3 | 16GB | `configs/xeon-4060ti/` | Batch Processing, Testing |

## Configuration Structure

Each machine has a dedicated configuration directory:

```
configs/
├── machines.json                 # Central registry of all machines
├── m4-macbook-pro/
│   ├── ai-router-config.json    # Machine-specific config
│   ├── models-manifest.json     # Installed models list
│   ├── setup.sh                 # Initial setup script
│   ├── venv/                    # Python virtual environment
│   ├── models/                  # Model files
│   ├── cache/                   # Cache directory
│   └── logs/                    # Application logs
├── ryzen-3900x-3090/
│   ├── ai-router-config.json
│   ├── models-manifest.json
│   ├── setup.sh
│   ├── venv/
│   ├── models/
│   ├── cache/
│   └── logs/
└── xeon-4060ti/
    ├── ai-router-config.json
    ├── models-manifest.json
    ├── setup.sh
    ├── venv/
    ├── models/
    ├── cache/
    └── logs/
```

## Quick Start Guide

### Option 1: Automatic Machine Detection

The system automatically detects which machine you're on:

```bash
python ai-router.py
# Automatically loads: configs/<machine-id>/ai-router-config.json
```

### Option 2: Run Setup Script (Recommended First Time)

Each machine has its own setup script:

**M4 MacBook Pro:**
```bash
bash configs/m4-macbook-pro/setup.sh
source configs/m4-macbook-pro/venv/bin/activate
python ai-router-mlx.py
```

**Ryzen 3900X + 3090:**
```bash
bash configs/ryzen-3900x-3090/setup.sh
source configs/ryzen-3900x-3090/venv/bin/activate
python ai-router.py
```

**Xeon E5 + 4060 Ti:**
```bash
bash configs/xeon-4060ti/setup.sh
source configs/xeon-4060ti/venv/bin/activate
python ai-router.py
```

## Machine Details

### M4 MacBook Pro (24GB)

**Config Location:** `configs/m4-macbook-pro/`

**Key Features:**
- MLX-optimized for Apple Silicon
- Portable development machine
- Conservative inference settings
- Not recommended for large batch processing

**Recommended Models:**
- `qwen25-coder-7b-mlx` (primary)
- `mistral-7b-mlx` (alternative)

**Setup:**
```bash
bash configs/m4-macbook-pro/setup.sh
```

**Run:**
```bash
source configs/m4-macbook-pro/venv/bin/activate
python ai-router-mlx.py
```

**Performance:**
- Max tokens: 2,048
- Batch size: 1
- Temperature: 0.7

**Notes:**
- Use MLX-specific models only
- Monitor thermal conditions during long runs
- Best for interactive development and testing

---

### Ryzen 3900X + RTX 3090 (64GB DDR4 + 24GB VRAM)

**Config Location:** `configs/ryzen-3900x-3090/`

**Key Features:**
- PRIMARY PRODUCTION MACHINE
- Highest overall performance in the cluster
- Full precision fp16 with Flash Attention v2
- Exceptional system RAM (64GB) for data processing
- Suitable for large batch processing and production inference

**Recommended Models:**
- `qwen25-coder-32b` (primary)
- `mistral-34b` (high performance)
- `llama2-70b` (with quantization for extended model size)

**Setup:**
```bash
bash configs/ryzen-3900x-3090/setup.sh
```

**Run:**
```bash
source configs/ryzen-3900x-3090/venv/bin/activate
python ai-router.py
```

**Performance Specs:**
- CPU: AMD Ryzen 3900X (12-core, 24-thread @ 3.8-4.6 GHz)
- RAM: 64GB DDR4 (excellent for preprocessing and caching)
- GPU: RTX 3090 (24GB VRAM)
- Max tokens: 4,096
- Batch size: 4
- Temperature: 0.7
- GPU Memory Utilization: 95%

**Notes:**
- Requires CUDA Toolkit 12.1+
- Run `nvidia-smi` to verify GPU detection
- Primary choice for production workloads
- Supports full-size models up to 70B parameters
- 64GB RAM allows for large dataset caching and preprocessing

---

### Xeon E5-2676v3 + RTX 4060 Ti (96GB DDR3 + 16GB VRAM)

**Config Location:** `configs/xeon-4060ti/`

**Key Features:**
- SERVER-CLASS MACHINE
- Massive 96GB DDR3 RAM (exceptional for batch processing and caching)
- Limited GPU VRAM (16GB) requires quantized models
- Perfect for data preprocessing and batch inference
- Chinese motherboard - may need driver adjustments
- Excellent for testing and validation workflows

**Recommended Models:**
- `qwen25-coder-7b` (Q4 quantized, primary)
- `mistral-7b` (Q4 quantized, alternative)
- `neural-chat-7b` (small footprint, ideal for batching)

**Setup:**
```bash
bash configs/xeon-4060ti/setup.sh
```

**Run:**
```bash
source configs/xeon-4060ti/venv/bin/activate
python ai-router.py
```

**Performance Specs:**
- CPU: Intel Xeon E5-2676v3 (12-core, 24-thread @ 2.4-3.5 GHz)
- RAM: 96GB DDR3 (excellent for large-scale data processing)
- GPU: RTX 4060 Ti (16GB VRAM)
- Max tokens: 2,048
- Batch size: 2
- Temperature: 0.7
- GPU Memory Utilization: 85%

**Best Use Cases:**
- Batch processing of large datasets
- Data preprocessing and feature engineering
- Model evaluation and testing workflows
- Quantized model inference
- Multiple sequential inference jobs
- Large dataset caching and buffering

**Notes:**
- Requires CUDA Toolkit 12.1+
- Quantization mandatory for GPU model loading (Q4 recommended)
- Can use CPU offloading for larger models
- 96GB RAM enables preprocessing of multi-gigabyte datasets
- Motherboard may require specific drivers - document any needed configuration
- Good for testing before production deployment on Ryzen machine

## Configuration Files

### machines.json

Central registry containing metadata for all machines:

```json
{
  "machines": [
    {
      "id": "m4-macbook-pro",
      "name": "M4 MacBook Pro",
      "cpu": "Apple M4 (8-core)",
      "platform": "Darwin (macOS)",
      "config_path": "configs/m4-macbook-pro/"
    }
  ]
}
```

### ai-router-config.json

Machine-specific configuration for models and inference:

```json
{
  "machine": {
    "id": "ryzen-9-3090",
    "name": "Ryzen 9 + RTX 3090"
  },
  "models": {
    "primary": "qwen25-coder-32b",
    "alternatives": ["dolphin-3-14b"]
  },
  "inference": {
    "backend": "vllm",
    "device": "cuda",
    "dtype": "float16"
  }
}
```

### models-manifest.json

Track which models are installed on each machine:

```json
{
  "machine_id": "ryzen-9-3090",
  "models": [
    {
      "name": "qwen25-coder-32b",
      "size": "16.4GB",
      "status": "ready",
      "installed": false
    }
  ]
}
```

## Machine Auto-Detection

The system includes automatic machine detection:

```python
def detect_machine():
    """Auto-detect which machine we're on"""
    if platform.system() == 'Darwin':  # macOS
        return 'm4-macbook-pro'

    # Linux - check CPU info
    with open('/proc/cpuinfo') as f:
        cpuinfo = f.read()
        if 'Ryzen' in cpuinfo:
            return 'ryzen-9-3090'
        elif 'Xeon' in cpuinfo:
            return 'xeon-4060ti'

    return None
```

The `.machine-id` file (created by setup scripts) overrides detection.

## Environment Variables by Machine

Set these in your shell profile (`.bashrc`, `.zshrc`, etc.):

**M4 MacBook Pro:**
```bash
export MACHINE_ID="m4-macbook-pro"
export VENV_PATH="configs/m4-macbook-pro/venv"
export MODELS_PATH="configs/m4-macbook-pro/models"
```

**Ryzen 3900X + 3090:**
```bash
export MACHINE_ID="ryzen-3900x-3090"
export VENV_PATH="configs/ryzen-3900x-3090/venv"
export MODELS_PATH="configs/ryzen-3900x-3090/models"
export CUDA_VISIBLE_DEVICES="0"
```

**Xeon E5 + 4060 Ti:**
```bash
export MACHINE_ID="xeon-4060ti"
export VENV_PATH="configs/xeon-4060ti/venv"
export MODELS_PATH="configs/xeon-4060ti/models"
export CUDA_VISIBLE_DEVICES="0"
```

## Git Workflow

Since all machines use the same repository:

### Committing Changes

1. **Machine-specific changes** go in the `configs/<machine-id>/` directory
2. **Shared code** stays in the root directory
3. **Test locally**, then commit:

```bash
git add .
git commit -m "Update Ryzen config: increase batch size to 4"
git push origin main
```

### After Pulling Updates

Each machine uses its own config, so `git pull` won't break anything:

```bash
git pull origin main
# Your local configs are automatically loaded
python ai-router.py
```

### Local-Only Files

These files are in `.gitignore` and stay local to each machine:

```
.machine-id
.local-config
configs/*/venv/          (Python virtual environment)
configs/*/cache/         (Model cache)
configs/*/logs/          (Log files)
*.db                     (Database files)
*.sqlite                 (SQLite files)
```

## Troubleshooting

### Machine Not Detected

If auto-detection fails:

```bash
# Manually set machine ID
echo "m4-macbook-pro" > .machine-id

# Then run
python ai-router.py
```

### Wrong Config Loaded

Check which machine was detected:

```bash
python -c "from configs import detect_machine; print(detect_machine())"
```

### Model Not Found

Check the models manifest:

```bash
cat configs/<machine-id>/models-manifest.json
```

### CUDA Issues (Linux machines)

```bash
# Check GPU detection
nvidia-smi

# Verify CUDA in Python
python -c "import torch; print(torch.cuda.is_available())"
```

## Documentation Files

- **MACHINE-SETUP.md** - This file (multi-machine setup)
- **MACHINE-PERFORMANCE.md** - Performance benchmarks by machine
- **MACBOOK-MLX-SETUP-GUIDE.md** - Detailed MacBook setup
- **MODEL-DEPLOYMENT-GUIDE-2025-12-16.md** - Model deployment guide

## Summary

1. **Single repository**, three machine configurations
2. **Auto-detection** identifies which machine you're on
3. **Isolated configs** prevent cross-contamination
4. **Easy to add new machines** - just create a new `configs/` subdirectory
5. **Full version history** - all machines tracked in git

Each machine is independent but coordinated through this shared framework.
