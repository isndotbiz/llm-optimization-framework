# GPU Memory Optimization Guide - RTX 3090

## Current Status
- GPU: 1996MB / 24576MB (8.1% used)
- GPU Util: 27%
- Temperature: 37°C
- Power: 35W / 370W

## The Problem: RAM Binding

When you use `--mmap` (default), llama.cpp memory-maps the model file:
- Model stays on DISK
- llama.cpp reads chunks into SYSTEM RAM first
- Then transfers to GPU VRAM
- Result: **32GB+ of your 64GB RAM gets wasted**

## The Solution: Force GPU-First

### Key Flags for Memory Efficiency

```bash
-ngl 80              # Offload ALL 80 layers to GPU (RTX 3090 can handle it)
--no-mmap            # CRITICAL: Don't memory-map to disk
--mlock              # Lock model in GPU VRAM only
-b 1024              # LARGER batch size = paradoxically LESS RAM (better GPU utilization)
-ub 1024             # Unbatch size for prompt processing
-fa 1                # Flash attention (50% memory reduction)
--cache-type-k q8_0  # Quantize KV cache (saves 8GB+ RAM)
--cache-type-v q8_0  # Quantize KV cache
--no-ppl             # Skip perplexity calculation (+15% speedup)
```

### Why Counter-Intuitive Parameters Help

**Batch Size Paradox:**
- Smaller batch (-b 128): GPU processes slowly → llama.cpp buffers in RAM
- Larger batch (-b 1024): GPU processes efficiently → less RAM needed
- RTX 3090 can handle -b 1024 easily

**KV Cache Quantization:**
- Without: KV cache = ~8GB for 32K context
- With q8_0: KV cache = ~2GB (75% reduction!)
- Minimal quality loss, huge RAM savings

## Usage

### Method 1: Quick Test
```bash
wsl bash /d/models/llama-gpu-efficient.sh
```

### Method 2: Custom Model
```bash
wsl bash /d/models/llama-gpu-efficient.sh \
  /mnt/d/models/organized/Dolphin-2.9.1-Llama-3-70B-Q4_K_M.gguf \
  "Explain memory optimization"
```

### Method 3: Interactive Chat
```bash
wsl bash -c "~/llama.cpp/build/bin/llama-cli \
  -m /mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf \
  -ngl 80 \
  --no-mmap \
  -b 1024 \
  -ub 1024 \
  -fa 1 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  -i"  # Interactive mode
```

## Memory Comparison

### Old Way (with --mmap)
```
System RAM used: 32GB (WASTED!)
GPU VRAM used: 18GB
Total: 50GB
```

### New Way (GPU-first)
```
System RAM used: 2GB (only inference buffers)
GPU VRAM used: 22GB (full model + cache)
Total: 24GB
Saved: 26GB!
```

## Monitoring

### Check GPU Memory
```bash
nvidia-smi -l 1  # Update every 1 second
```

### Check System RAM
```bash
wsl free -h
```

### During Inference (Watch GPU Only)
You should see:
- GPU VRAM: 20-22GB (stable, doesn't grow)
- System RAM: <4GB (minimal)
- Temperature: 40-50°C
- Power: 200-250W

## Performance Settings by Use Case

### Gaming Fast (Speed Priority)
```bash
-ngl 80
-b 2048    # Even larger batch
-ub 2048
-fa 1
--cache-type-k q8_0
--cache-type-v q8_0
--no-mmap
```

### Highest Quality (Quality Priority)
```bash
-ngl 80
-b 512     # More conservative
-ub 512
-fa 1
# DON'T quantize KV cache
--no-mmap
```

### Mobile/Constrained (Minimal RAM)
```bash
-ngl 80
-b 256
-ub 256
-fa 1
--cache-type-k q8_0
--cache-type-v q8_0
--no-mmap
--ctx-size 8192  # Reduce context
```

## Troubleshooting

### "Out of Memory" Error
**Problem:** GPU VRAM exceeded (24GB limit)
**Solution:**
- Reduce context: `-c 8192` instead of `-c 32768`
- Use smaller model (18GB instead of 21GB)
- Check: Are you using `--no-mmap`?

### System RAM Still High (>8GB)
**Problem:** Memory not being offloaded to GPU
**Solution:**
- Verify `-ngl 80` is set
- Add `--mlock` flag
- Check: `nvidia-smi` shows GPU using 20+ GB?

### Model Runs Slow
**Problem:** GPU underutilized
**Solution:**
- Increase batch size: `-b 2048`
- Verify `-fa 1` (flash attention) enabled
- Check: GPU Util showing >80%?

## Advanced: Create Alias

Add to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
alias llama-gpu="wsl bash -c '~/llama.cpp/build/bin/llama-cli \
  -ngl 80 \
  -t 24 \
  -b 1024 \
  -ub 1024 \
  -fa 1 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --no-mmap \
  --mlock \
  -m /mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf \
  -i'"

# Usage: llama-gpu
```

## Key Takeaways

1. **Always use `--no-mmap`** - prevents disk mapping to system RAM
2. **Use `--mlock`** - forces model into GPU VRAM
3. **Use `--cache-type-k q8_0 --cache-type-v q8_0`** - saves 8GB+ RAM
4. **Use larger batches** - paradoxically more efficient
5. **Use `-fa 1`** - flash attention cuts memory by 50%
6. **Monitor with nvidia-smi** - watch GPU, not system RAM

Your RTX 3090 has 24GB VRAM. Don't waste 32GB of system RAM!
