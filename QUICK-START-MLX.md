# MLX Quick Start Guide

Fast reference for using MLX models after migration.

## One-Line Setup

```bash
source mlx/venv/bin/activate
```

## Common Commands

### Fast Coding (60-80 tok/sec)
```bash
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit
```

### General Questions (40-60 tok/sec)
```bash
mlx_lm.chat --model mlx-community/Qwen3-14B-Instruct-4bit
```

### Math & Reasoning (50-70 tok/sec)
```bash
mlx_lm.chat --model mlx-community/DeepSeek-R1-Distill-Llama-8B
```

### Ultra-Fast (70-100 tok/sec)
```bash
mlx_lm.chat --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

### Complex Coding (11-22 tok/sec, needs 32GB+ RAM)
```bash
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-32B-Instruct-4bit
```

## Recommended Aliases

Add to `~/.zshrc`:

```bash
alias mlx='source ~/Workspace/llm-optimization-framework/mlx/venv/bin/activate'
alias code-fast='mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit'
alias chat='mlx_lm.chat --model mlx-community/Qwen3-14B-Instruct-4bit'
alias math='mlx_lm.chat --model mlx-community/DeepSeek-R1-Distill-Llama-8B'
alias turbo='mlx_lm.chat --model mlx-community/Mistral-7B-Instruct-v0.3-4bit'
```

Then use:
```bash
mlx          # Activate environment
code-fast    # Quick coding
chat         # General chat
math         # Math/reasoning
turbo        # Ultra-fast
```

## Performance vs Ollama

| Task | Old (Ollama) | New (MLX) | Speedup |
|------|-------------|-----------|---------|
| Coding | 20-30 tok/sec | 60-80 tok/sec | 3x faster |
| Math | 10-15 tok/sec | 50-70 tok/sec | 5x faster |
| General | 20-30 tok/sec | 40-60 tok/sec | 2x faster |

## Model Selection Guide

**Choose Qwen2.5-Coder-7B when:**
- Quick code fixes
- Daily coding tasks
- You want speed

**Choose Qwen3-14B when:**
- Research questions
- Writing documentation
- Balanced quality/speed

**Choose DeepSeek-R1-8B when:**
- Math problems
- Logical reasoning
- Problem decomposition

**Choose Mistral-7B when:**
- Ultra-fast responses needed
- Simple queries
- Resource-constrained

**Choose Qwen2.5-Coder-32B when:**
- Complex architecture design
- Advanced coding tasks
- You have 32GB+ RAM available

## Troubleshooting

**Models not found?**
```bash
# Check downloads
ls -lh mlx/

# Download missing model
huggingface-cli download mlx-community/Qwen2.5-Coder-7B-Instruct-4bit --local-dir mlx/qwen25-coder-7b
```

**Slow performance?**
```bash
# Check if other apps using GPU
# Close Chrome, heavy apps
# Monitor with Activity Monitor
```

**Out of memory?**
```bash
# Use smaller model
mlx_lm.chat --model mlx-community/Qwen3-7B-Instruct-4bit

# Or ultra-light
mlx_lm.chat --model mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

## Tips

1. **First time?** Models auto-download from cache
2. **Interrupted download?** Just run again, resumes automatically
3. **Switch models?** Press Ctrl+D or type `exit`
4. **Best speed?** Close other GPU-heavy apps
5. **Save responses?** Use `> output.txt` redirection

## Speed Comparison

```
Ollama GGUF (old):
  Qwen-Coder: ████░░░░░░ 20-30 tok/sec
  DeepSeek:   ██░░░░░░░░ 10-15 tok/sec

MLX (new):
  Qwen-Coder: ████████░░ 60-80 tok/sec
  DeepSeek:   ███████░░░ 50-70 tok/sec
```

## Need Help?

See full documentation:
```bash
cat OLLAMA-TO-MLX-CONVERSION.md
```
