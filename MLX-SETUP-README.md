# MLX Automated Setup Scripts

Comprehensive automated installation scripts for MLX on Apple Silicon MacBooks (M1/M2/M3/M4).

## Quick Start

```bash
# Run the automated setup (recommended)
./setup-mlx-macbook.sh

# Or run validation only
python3 setup_mlx_environment.py --validate
```

## What Gets Installed

### 1. Python Virtual Environment
- Location: `~/venv-mlx`
- Python 3.9+ with isolated dependencies
- Clean separation from system Python

### 2. MLX Packages
- **mlx** - Core MLX framework optimized for Apple Silicon
- **mlx-lm** - Language model utilities and inference
- **numpy** - Numerical computing
- **transformers** - Hugging Face transformers
- **huggingface-hub** - Model downloading
- **sentencepiece** - Tokenization
- **tiktoken** - OpenAI tokenizer

### 3. Directory Structure
```
~/
├── venv-mlx/              # Python virtual environment
└── workspace/
    └── mlx/               # MLX models storage
```

### 4. Shell Configuration
Adds to `~/.zshrc` or `~/.bashrc`:
- Environment variables
- Convenience aliases
- Helper functions

## Scripts Overview

### setup-mlx-macbook.sh
Main installation script that orchestrates the entire setup process.

**Features:**
- ✅ Pre-flight system checks (macOS, Apple Silicon, Python version)
- ✅ Disk space and memory validation
- ✅ Virtual environment creation
- ✅ MLX package installation
- ✅ Directory structure setup
- ✅ Shell configuration (aliases, functions)
- ✅ Installation validation
- ✅ Idempotent (safe to run multiple times)
- ✅ Comprehensive error handling
- ✅ Color-coded output

**Usage:**
```bash
# Full installation
./setup-mlx-macbook.sh

# The script will:
# 1. Check system requirements
# 2. Create virtual environment
# 3. Install MLX and dependencies
# 4. Configure shell environment
# 5. Run validation tests
# 6. Display next steps
```

### setup_mlx_environment.py
Python-side validation and model management.

**Features:**
- ✅ MLX core installation validation
- ✅ Metal GPU support verification
- ✅ Performance benchmarking
- ✅ Model download management
- ✅ Dependency checking
- ✅ System information display

**Usage:**
```bash
# Full validation suite
python3 setup_mlx_environment.py --validate

# Performance benchmark
python3 setup_mlx_environment.py --benchmark

# List recommended models
python3 setup_mlx_environment.py --list-models

# Download a model
python3 setup_mlx_environment.py --download-model qwen25-coder-7b

# Quiet mode (minimal output)
python3 setup_mlx_environment.py --validate --quiet
```

## Shell Aliases and Functions

After installation, these commands are available:

### Environment Management
```bash
mlx-activate      # Activate MLX virtual environment
mlx-status        # Check MLX installation status
mlx-validate      # Run full validation suite
mlx-models        # List available models
```

### Quick Model Access
```bash
# Text generation
mlx-qwen7b --prompt "Write a Python function..."
mlx-qwen32b --prompt "Design a system architecture..."
mlx-deepseek --prompt "Solve this math problem..."
mlx-phi4 --prompt "Explain quantum computing..."

# Interactive chat
mlx-chat-qwen7b
mlx-chat-qwen32b
mlx-chat-deepseek
mlx-chat-phi4
```

## Model Recommendations

### Fast Daily Coding (Recommended)
**Qwen2.5 Coder 7B** - `mlx-chat-qwen7b`
- Size: 4.5GB
- Speed: 60-80 tokens/sec
- Best for: Code review, quick iterations, debugging

### Best Quality
**Qwen2.5 Coder 32B** - `mlx-chat-qwen32b`
- Size: 18GB
- Speed: 11-22 tokens/sec
- Best for: Architecture design, complex refactoring
- Requires: 24GB+ RAM

### Reasoning & Math
**DeepSeek-R1 8B** - `mlx-chat-deepseek`
- Size: 4.5GB
- Speed: 50-70 tokens/sec
- Best for: Problem solving, analysis, math

**Phi-4 14B** - `mlx-chat-phi4`
- Size: 8-9GB
- Speed: 40-60 tokens/sec
- Best for: Math, algorithms, technical explanations

## Validation Checks

The validation script performs these checks:

1. **System Information**
   - OS version and architecture
   - Python version
   - Total RAM
   - MLX version

2. **MLX Core**
   - Import verification
   - Version check
   - Basic array operations
   - Default device detection

3. **Metal GPU Support**
   - GPU device detection
   - Metal backend availability
   - GPU computation test

4. **mlx-lm Package**
   - Import verification
   - Core functions availability
   - API compatibility

5. **Dependencies**
   - NumPy
   - Transformers
   - Hugging Face Hub

6. **Performance (Optional)**
   - Matrix multiplication benchmark
   - GFLOPS calculation
   - Average operation time

## Troubleshooting

### Virtual Environment Not Activating
```bash
# Manual activation
source ~/venv-mlx/bin/activate

# Or use alias (after reloading shell)
source ~/.zshrc
mlx-activate
```

### MLX Not Found After Installation
```bash
# Ensure you're in the virtual environment
mlx-activate

# Verify installation
python3 -c "import mlx.core as mx; print(mx.__version__)"

# Reinstall if needed
pip install --upgrade mlx mlx-lm
```

### Metal GPU Not Detected
```bash
# Check default device
python3 -c "import mlx.core as mx; print(mx.default_device())"

# Should show 'gpu' or 'metal'
# If shows 'cpu', check:
# 1. Running on Apple Silicon (M1/M2/M3/M4)?
# 2. macOS version (needs macOS 13+)
```

### Import Errors
```bash
# Check which Python is being used
which python3
# Should be: ~/venv-mlx/bin/python3

# If not, activate environment
mlx-activate
```

### Disk Space Issues
```bash
# Check available space
df -h ~

# Models are large:
# - Qwen 7B: ~4.5GB
# - Qwen 32B: ~18GB
# - Phi-4: ~8-9GB

# Move models to external drive if needed
ln -s /Volumes/External/mlx ~/workspace/mlx
```

## Performance Expectations

### M4 MacBook Pro
| Model | Load Time | First Token | Speed | Memory |
|-------|-----------|-------------|-------|---------|
| Qwen 7B | <500ms | <300ms | 60-80 tok/sec | 2-3GB |
| Qwen 32B | 1-2s | <500ms | 11-22 tok/sec | 8-12GB |
| DeepSeek-R1 | <500ms | <300ms | 50-70 tok/sec | 2-3GB |
| Phi-4 | <1s | <400ms | 40-60 tok/sec | 4-6GB |

### M3/M2/M1 Performance
- Expect 10-20% slower than M4
- Still 2-3x faster than Ollama
- Memory usage similar

## Uninstallation

```bash
# Remove virtual environment
rm -rf ~/venv-mlx

# Remove models (WARNING: large files)
rm -rf ~/workspace/mlx

# Remove shell configuration
# Edit ~/.zshrc or ~/.bashrc and remove the section:
# # MLX Environment Configuration
# ... (all lines until)
# # End MLX Configuration
```

## Advanced Usage

### Custom Model Paths
```bash
# Set custom model directory
export MLX_MODELS_PATH="/path/to/models"

# Download model to custom location
python3 setup_mlx_environment.py --download-model qwen25-coder-7b
```

### Offline Usage
```bash
# Download models while online
mlx_lm.download --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit

# Use offline (models cached in ~/.cache/huggingface)
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit
```

### Custom Temperature and Parameters
```bash
mlx_lm.generate \
  --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit \
  --prompt "Your prompt" \
  --temp 0.7 \
  --max-tokens 2048 \
  --top-p 0.9
```

## Integration with AI Router

The scripts are designed to work seamlessly with the AI Router system:

```bash
# After setup, run AI Router
mlx-activate
python3 ~/workspace/llm-optimization-framework/ai-router-mlx.py
```

## System Requirements

### Minimum
- macOS 13.0+
- Apple Silicon (M1/M2/M3/M4)
- 16GB RAM
- 20GB free disk space
- Python 3.9+

### Recommended
- macOS 14.0+
- M3 or M4 chip
- 32GB+ RAM
- 50GB+ free disk space (for multiple models)
- Python 3.11+

## Why MLX?

### vs Ollama
- **3-4x faster** on Apple Silicon
- **Lower memory** usage (2-3GB vs 4-6GB)
- **No daemon** required
- **Direct control** over parameters
- **Native Apple** Metal integration

### vs llama.cpp
- **2-3x faster** on M-series chips
- **Better Metal** optimization
- **Simpler API** for Python
- **First-class Apple** Silicon support

## Contributing

If you encounter issues or have improvements:

1. Check existing issues in the project
2. Run validation with verbose output: `python3 setup_mlx_environment.py --validate`
3. Include system info: `mlx-status`
4. Provide error logs

## License

These scripts are part of the llm-optimization-framework project.

## Support

For questions or issues:
- Check MACBOOK-MLX-SETUP-GUIDE.md for manual setup
- Run `mlx-validate` for diagnostic information
- Check MLX documentation: https://ml-explore.github.io/mlx/
