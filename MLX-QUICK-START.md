# MLX Quick Start Guide

## Installation (One Command)

```bash
./setup-mlx-macbook.sh
```

That's it! The script handles everything automatically.

## After Installation

### 1. Reload Your Shell
```bash
source ~/.zshrc  # or ~/.bashrc
```

### 2. Activate MLX
```bash
mlx-activate
```

### 3. Verify Installation
```bash
mlx-status
mlx-validate
```

## Daily Usage

### Start Coding with Qwen 7B (Recommended)
```bash
mlx-activate
mlx-chat-qwen7b
```

### Check Available Models
```bash
mlx-models
```

### Quick Text Generation
```bash
mlx-qwen7b --prompt "Write a Python function to parse JSON"
```

## Common Commands

| Command | Purpose |
|---------|---------|
| `mlx-activate` | Activate MLX environment |
| `mlx-status` | Check installation status |
| `mlx-validate` | Run full validation |
| `mlx-models` | List available models |
| `mlx-chat-qwen7b` | Fast coding (60-80 tok/sec) |
| `mlx-chat-qwen32b` | Best quality (11-22 tok/sec) |
| `mlx-chat-deepseek` | Math & reasoning |
| `mlx-chat-phi4` | Math & algorithms |

## Model Selection Guide

**For Quick Code Review & Debugging**
→ `mlx-chat-qwen7b` (4.5GB, ultra-fast)

**For Complex Architecture & Design**
→ `mlx-chat-qwen32b` (18GB, best quality, needs 24GB+ RAM)

**For Math Problems & Reasoning**
→ `mlx-chat-deepseek` (4.5GB, reasoning specialist)

**For Technical Explanations**
→ `mlx-chat-phi4` (8-9GB, math focused)

## Troubleshooting One-Liners

```bash
# Not working? Activate first!
mlx-activate

# Check if MLX is installed
python3 -c "import mlx.core as mx; print(mx.__version__)"

# Check GPU support
python3 -c "import mlx.core as mx; print(mx.default_device())"

# Reinstall MLX
pip install --upgrade mlx mlx-lm

# Full validation
python3 setup_mlx_environment.py --validate
```

## Performance Expectations (M4 MacBook Pro)

- **Load Time**: <1 second
- **First Token**: <500ms
- **Speed**: 60-80 tokens/sec (Qwen 7B)
- **Memory**: 2-3GB (Qwen 7B)

**3-4x faster than Ollama on M4!**

## Next Steps

1. Run a test chat: `mlx-chat-qwen7b`
2. Try the AI Router: `python3 ai-router-mlx.py`
3. Download more models: See MLX-SETUP-README.md

## Full Documentation

- **Setup Guide**: MACBOOK-MLX-SETUP-GUIDE.md
- **Complete Manual**: MLX-SETUP-README.md
- **Scripts Documentation**: Comments in setup-mlx-macbook.sh

## Support

Having issues? Run diagnostics:
```bash
mlx-status
mlx-validate
```

Include output when asking for help!
