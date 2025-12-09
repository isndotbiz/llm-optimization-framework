# MacBook M4 Pro Optimization Guide (24GB Unified Memory)

## Hardware Specifications

**Your MacBook M4 Pro:**
- CPU: 12 cores (8 performance + 4 efficiency)
- GPU: 16 cores
- Unified Memory: 24GB (shared between CPU and GPU)
- Memory Bandwidth: ~273 GB/s

**vs RTX 3090:**
- RTX 3090: 24GB dedicated VRAM, ~936 GB/s bandwidth
- M4: 24GB unified memory, ~273 GB/s bandwidth
- **Key difference**: Unified memory architecture vs dedicated VRAM

---

## Best Framework: MLX (Apple's Framework)

**Why MLX over llama.cpp on Mac:**
- **2-3x faster** than llama.cpp Metal backend
- Designed specifically for Apple Silicon
- Optimized for unified memory architecture
- Better GPU utilization on M-series chips
- Native fp16 support
- Excellent quantization support

**Performance Comparison (M4 Pro):**
- **MLX**: 50-80 tok/sec (Qwen 14B Q4)
- **llama.cpp Metal**: 20-35 tok/sec (same model)
- **Ollama**: 25-40 tok/sec (uses llama.cpp Metal)

---

## Installation (macOS)

### Install MLX

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Create virtual environment
python3 -m venv ~/mlx_venv
source ~/mlx_venv/bin/activate

# Install MLX and dependencies
pip install mlx mlx-lm huggingface_hub

# Verify installation
python3 -c "import mlx.core as mx; print(mx.metal.is_available())"
```

### Alternative: llama.cpp with Metal

```bash
# Clone and build llama.cpp
cd ~
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make clean
LLAMA_METAL=1 make -j

# Verify Metal support
./llama-cli --version | grep Metal
```

---

## Optimal Models for M4 Pro (24GB)

### Recommended Models (Priority Order)

#### 1. **Qwen2.5-14B-Instruct** (BEST for general use)
- **Quantization**: Q4_K_M or Q5_K_M
- **Size**: 8-11GB
- **Performance**: 50-70 tok/sec (MLX)
- **Use case**: General chat, research, instruction following
- **Download**:
```bash
huggingface-cli download Qwen/Qwen2.5-14B-Instruct-GGUF \
  --include "*q4_k_m.gguf" \
  --local-dir ~/models/qwen25-14b
```

#### 2. **Qwen2.5-Coder-14B** (BEST for coding)
- **Quantization**: Q4_K_M
- **Size**: 8GB
- **Performance**: 50-75 tok/sec (MLX)
- **Use case**: Code generation, debugging, technical tasks
- **Download**:
```bash
huggingface-cli download Qwen/Qwen2.5-Coder-14B-Instruct-GGUF \
  --include "*q4_k_m.gguf" \
  --local-dir ~/models/qwen25-coder-14b
```

#### 3. **Llama-3.3-70B-Instruct** (For maximum capability)
- **Quantization**: IQ2_S or IQ2_M (aggressive)
- **Size**: 18-22GB
- **Performance**: 15-25 tok/sec (MLX)
- **Use case**: Complex reasoning, research, when quality > speed
- **Download**:
```bash
huggingface-cli download bartowski/Llama-3.3-70B-Instruct-GGUF \
  --include "*IQ2_M.gguf" \
  --local-dir ~/models/llama33-70b
```

#### 4. **Qwen2.5-32B** (Balanced power)
- **Quantization**: Q3_K_M or Q4_K_S
- **Size**: 13-20GB
- **Performance**: 30-45 tok/sec (MLX)
- **Use case**: Complex tasks, creative writing, analysis
- **Download**:
```bash
huggingface-cli download Qwen/Qwen2.5-32B-Instruct-GGUF \
  --include "*q4_k_s.gguf" \
  --local-dir ~/models/qwen25-32b
```

#### 5. **Phi-4-14B** (Fast reasoning)
- **Quantization**: Q6_K or Q8_0
- **Size**: 10-16GB
- **Performance**: 45-65 tok/sec (MLX)
- **Use case**: Math, reasoning, STEM tasks
- **Download**:
```bash
huggingface-cli download microsoft/Phi-4-GGUF \
  --include "*q6_k.gguf" \
  --local-dir ~/models/phi4-14b
```

#### 6. **Gemma-3-9B** (Speed champion)
- **Quantization**: Q6_K or Q8_0
- **Size**: 7-10GB
- **Performance**: 70-100 tok/sec (MLX)
- **Use case**: Fast responses, chat, general queries
- **Download**:
```bash
huggingface-cli download google/gemma-3-9b-GGUF \
  --include "*q6_k.gguf" \
  --local-dir ~/models/gemma3-9b
```

---

## Comparison: M4 vs RTX 3090

### What You CAN Run (Same or Better)

| Model Size | RTX 3090 Quant | M4 Pro Quant | Performance |
|-----------|----------------|--------------|-------------|
| **8-14B models** | Q6_K | Q6_K | ✅ **M4 similar or better** |
| **14-32B models** | Q4_K_M | Q4_K_M | ⚠️ **3090 faster (2-3x)** |
| **70B models** | IQ2_S | IQ2_M | ⚠️ **3090 much faster (3-5x)** |

### What You CANNOT Run (vs 3090)

- ❌ **Multiple large models simultaneously** (3090 handles better)
- ❌ **70B Q4+ quantization** (too large for 24GB)
- ❌ **Ultra-long context (128K+)** with large models (memory bandwidth limited)

### M4 Advantages

- ✅ **Better power efficiency** (10-15W vs 350W)
- ✅ **Quieter operation** (no fans at load)
- ✅ **Unified memory** (no CPU-GPU transfer overhead)
- ✅ **Portable** (can run anywhere)
- ✅ **8-14B models run excellently**

---

## Optimal Parameters (M4 Pro)

### MLX Parameters

```bash
mlx_lm.generate \
  --model ~/models/qwen25-14b \
  --max-tokens 2048 \
  --temp 0.7 \
  --top-p 0.9 \
  --prompt "Your prompt here"
```

### llama.cpp Metal Parameters

```bash
./llama-cli \
  -m ~/models/model.gguf \
  -ngl 99 \              # Offload all layers to GPU
  -t 6 \                 # Use 6 performance cores
  -b 512 \               # Batch size
  --no-mmap \            # Disable memory mapping (faster on M4)
  --temp 0.7 \
  --top-p 0.9 \
  -p "Your prompt here"
```

**Key Differences from Windows/WSL:**
- **No `-fa` flag** (Flash Attention automatic on Metal)
- **`--no-mmap`** often faster on Apple Silicon
- **Lower thread count** (6-8 cores, not 24)
- **Smaller batch sizes** (512 vs 2048)

---

## Quantization Guide for M4

### Recommended Quantization Levels

| Model Size | Optimal Quant | File Size | Speed | Quality |
|-----------|---------------|-----------|-------|---------|
| **7-9B** | Q6_K or Q8_0 | 7-10GB | Excellent | Excellent |
| **14B** | Q5_K_M or Q6_K | 9-12GB | Excellent | Excellent |
| **32B** | Q4_K_M or Q4_K_S | 13-18GB | Good | Good |
| **70B** | IQ2_M or IQ2_S | 18-22GB | Slow | Acceptable |

### Quality Hierarchy (M4)

**Best to Worst:**
Q8_0 > Q6_K > Q5_K_M > IQ4_K > Q4_K_M > Q4_K_S > IQ3_M > Q3_K_M > IQ2_M > IQ2_S

**Avoid on M4:**
- Q2_K and below (quality too degraded)
- F16/F32 (too large, no benefit)

---

## Performance Benchmarks (M4 Pro 24GB)

### MLX Performance

| Model | Quantization | Prompt Eval | Generation | Memory |
|-------|--------------|-------------|------------|--------|
| Qwen2.5-14B | Q4_K_M | 180-220 tok/s | 55-70 tok/s | 9GB |
| Qwen2.5-32B | Q4_K_S | 80-100 tok/s | 30-40 tok/s | 18GB |
| Llama-3.3-70B | IQ2_M | 35-45 tok/s | 15-22 tok/s | 22GB |
| Phi-4-14B | Q6_K | 200-250 tok/s | 60-75 tok/s | 12GB |
| Gemma-3-9B | Q6_K | 280-320 tok/s | 85-110 tok/s | 8GB |

**Note**: Prompt eval = processing your input, Generation = producing output

---

## Memory Management

### Monitor Memory Usage

```bash
# Check memory pressure
memory_pressure

# Monitor in real-time
sudo powermetrics --samplers gpu_power,cpu_power -i 1000

# Activity Monitor
open -a "Activity Monitor"
```

### Optimize Memory

1. **Close unnecessary apps** before running large models
2. **Disable browser** (can use 4-8GB)
3. **Use smaller quantization** if memory warnings appear
4. **Monitor swap usage** - avoid heavy swapping

---

## Recommended Model Set for M4

**Primary Models (Download These):**

1. **Qwen2.5-14B-Instruct Q5_K_M** (11GB) - Daily driver
2. **Qwen2.5-Coder-14B Q4_K_M** (8GB) - Coding tasks
3. **Phi-4-14B Q6_K** (12GB) - Reasoning/math
4. **Gemma-3-9B Q6_K** (8GB) - Fast responses

**Optional (If space allows):**

5. **Llama-3.3-70B IQ2_M** (22GB) - Maximum capability
6. **Qwen2.5-32B Q4_K_S** (18GB) - Power user

**Total Storage**: ~60-80GB for full set

---

## MLX vs llama.cpp Decision Matrix

| Use Case | Recommended Framework | Reason |
|----------|----------------------|--------|
| **Best performance** | MLX | 2-3x faster on Apple Silicon |
| **Maximum compatibility** | llama.cpp | Supports all GGUF models |
| **Easiest setup** | Ollama | One-command install |
| **Fine-tuning** | MLX | Supports LoRA training |
| **Cross-platform** | llama.cpp | Works everywhere |
| **Latest models** | MLX | Often has early support |

---

## Sample Commands

### Using MLX

```bash
# Interactive chat
mlx_lm.chat --model ~/models/qwen25-14b

# Single generation
mlx_lm.generate \
  --model ~/models/qwen25-14b \
  --prompt "Explain quantum computing" \
  --max-tokens 1000 \
  --temp 0.7

# With system prompt
mlx_lm.generate \
  --model ~/models/qwen25-14b \
  --system-prompt "You are a helpful AI assistant specialized in research" \
  --prompt "Your question here"
```

### Using llama.cpp Metal

```bash
# Interactive mode
./llama-cli \
  -m ~/models/qwen25-14b-q5_k_m.gguf \
  -ngl 99 \
  -t 6 \
  --interactive \
  --temp 0.7

# Single prompt
./llama-cli \
  -m ~/models/qwen25-14b-q5_k_m.gguf \
  -ngl 99 \
  -t 6 \
  -p "Explain quantum computing" \
  -n 1000 \
  --temp 0.7
```

---

## Troubleshooting

### Model Too Slow

- ✅ Use smaller quantization (Q4 instead of Q6)
- ✅ Use smaller model (14B instead of 32B)
- ✅ Switch to MLX if using llama.cpp
- ✅ Close background apps
- ✅ Reduce batch size (`-b 256`)

### Out of Memory

- ✅ Use more aggressive quantization (IQ2 for 70B)
- ✅ Use smaller model
- ✅ Close all other apps
- ✅ Reduce context size (`-c 4096`)
- ✅ Check Activity Monitor for memory leaks

### Poor Quality Outputs

- ✅ Use higher quantization (Q6_K instead of Q4)
- ✅ Use larger model (32B instead of 14B)
- ✅ Adjust temperature (try 0.6-0.8)
- ✅ Improve system prompt
- ✅ Check you're not using IQ2/Q2 quants

---

## Best Practices for M4

1. **Start with 14B Q5_K_M models** - best balance
2. **Use MLX for daily work** - significantly faster
3. **Keep llama.cpp for compatibility** - some models MLX doesn't support
4. **Monitor memory pressure** - avoid heavy swapping
5. **Prefer quality over size** - 14B Q6 > 32B Q3
6. **Use SSD storage** - models load faster
7. **Keep macOS updated** - Metal improvements in each release

---

## Conclusion

**Your M4 Pro is excellent for:**
- ✅ 8-14B models (near-RTX 3090 performance)
- ✅ Coding, research, general tasks
- ✅ Portable, power-efficient AI work
- ✅ Fast iteration and experimentation

**RTX 3090 is better for:**
- 🚀 30B+ models (2-3x faster)
- 🚀 70B models (3-5x faster)
- 🚀 Ultra-long context windows
- 🚀 Heavy batch processing

**Recommendation**: Use your M4 for daily work with 8-14B models, and your RTX 3090 Windows machine for heavy-duty 30B+ model work.

---

**Document Version**: 1.0
**Last Updated**: 2025-12-08
**Hardware**: M4 Pro (12 CPU/16 GPU cores, 24GB unified memory)
