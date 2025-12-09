# 🎯 Complete 2025 LLM Setup Summary
**Last Updated**: December 8, 2025  
**Hardware**: RTX 3090 24GB + RTX 4060 Ti 16GB + Ryzen 9 5900X + 64GB RAM

---

## ✅ Complete Model Collection

### RTX 3090 (24GB) - 9 Models (~107GB)

| # | Model | Size | Use Case |
|---|-------|------|----------|
| 1 | **Llama-3.3-70B-Instruct-abliterated** (IQ2_S) | 21GB | Best uncensored reasoning, complex research |
| 2 | **Qwen3-Coder-30B** (Q4_K_M) | 18GB | Advanced coding (94% HumanEval), 256K context |
| 3 | **Dolphin-Mistral-24B-Venice** (Q4_K_M) | 14GB | Lowest refusal rate (2.2%) |
| 4 | **Phi-4-Reasoning-Plus** ⭐ (Q6_K) | 12GB | Math & logic (78% AIME 2025) |
| 5 | **DeepSeek-R1-Distill-Qwen-14B** (Q5_K_M) | 9.8GB | Chain-of-thought reasoning (94.3% MATH-500) |
| 6 | **Gemma-3-27B-Abliterated** ⭐ (Q2_K) | 9.8GB | Creative writing, 128K context |
| 7 | **Ministral-3-14B-Reasoning** ⭐ (Q5_K_M) | 9GB | Best reasoning at 14B (85% AIME), 256K context |
| 8 | **Wizard-Vicuna-13B-Uncensored** (Q4_0) | 6.9GB | Classic uncensored general purpose |
| 9 | **Dolphin3.0-Llama3.1-8B** (Q6_K) | 6.2GB | Fast uncensored 8B - 60-90 tok/sec |

### RTX 4060 Ti (16GB) - 5 Models (~34GB)

| # | Model | Size | Use Case |
|---|-------|------|----------|
| 1 | **Qwen2.5-14B-Instruct** (Q4_K_M) | 8.4GB | Smart daily driver with safety filters |
| 2 | **Qwen2.5-14B-Uncensored** (Q4_K_M) | 8.4GB | Uncensored daily driver for server |
| 3 | **Meta-Llama-3.1-8B-Instruct** (Q6_K) | 6.2GB | Production-ready, Meta official |
| 4 | **Dolphin3.0-Llama3.1-8B** (Q6_K) | 6.2GB | Server backup - fast uncensored |
| 5 | **Qwen2.5-Coder-7B** (Q5_K_M) | 5.1GB | Fast coding specialist (84.8% HumanEval) |

⭐ = New models added December 8, 2025

**Total Storage**: ~141GB across 14 models  
**Space Freed**: 41GB (deleted old Qwen2.5-Coder-32B, phi-4, mythomax)

---

## 📚 Complete Documentation Suite

### Core Configuration Files
1. ✅ **LLAMA-CPP-OPTIMAL-PARAMS.lock** (12KB) - Locked 2025 research parameters
2. ✅ **2025-RESEARCH-SUMMARY.md** (18KB) - Comprehensive research findings
3. ✅ **MODEL-PARAMETERS-QUICK-REFERENCE.json** (6.5KB) - All model parameters
4. ✅ **SYSTEM-PROMPTS-QUICK-START.md** (7KB) - Quick reference guide
5. ✅ **OPTIMIZED-SYSTEM-PROMPTS-2025-RESEARCH-BASED.txt** (51KB) - Master documentation

### System Prompt Files (13 files)
**RTX 3090** (D:\models\organized\):
- Llama-3.3-70B-SYSTEM-PROMPT.txt
- Qwen3-Coder-30B-SYSTEM-PROMPT.txt
- Dolphin-Mistral-24B-SYSTEM-PROMPT.txt
- Phi-4-Reasoning-Plus-SYSTEM-PROMPT.txt
- Gemma-3-27B-SYSTEM-PROMPT.txt (special: CO-STAR framework)
- Ministral-3-14B-SYSTEM-PROMPT.txt
- DeepSeek-R1-SYSTEM-PROMPT.txt (special: user prompt only)
- Wizard-Vicuna-13B-SYSTEM-PROMPT.txt
- Dolphin-3.0-8B-SYSTEM-PROMPT.txt

**RTX 4060 Ti** (D:\models\rtx4060ti-16gb\):
- Qwen-14B-Instruct-SYSTEM-PROMPT.txt
- Qwen-14B-Uncensored-SYSTEM-PROMPT.txt
- Llama-3.1-8B-SYSTEM-PROMPT.txt
- Qwen-Coder-7B-SYSTEM-PROMPT.txt

### Automation Scripts
1. ✅ **RUN-MODEL-WITH-PROMPT.ps1** (8.6KB) - Automated model runner
2. ✅ **VALIDATE-CONFIG.ps1** (9.8KB) - Configuration validator
3. ✅ **MONITOR-PERFORMANCE.ps1** (8.1KB) - Performance monitoring
4. ✅ **ENSURE-WSL-USAGE.ps1** (6.3KB) - WSL verification
5. ✅ **CREATE-SYSTEM-PROMPTS.ps1** (7.2KB) - System prompt generator

---

## 🚀 2025 Research Key Findings

### Performance Breakthroughs
- ✅ **WSL Performance**: Within 1% of native Linux for GPU workloads
- ✅ **GPU Layers**: Use `-ngl 999` (not 99) for full offload
- ✅ **Batch Size**: Minimum 512, optimal 512-2048
- ✅ **Flash Attention**: `-fa 1` provides +20% speed, 50% memory savings
- ✅ **KV Cache**: `--cache-type-k q8_0` gives 50% memory reduction
- ✅ **IQ Quantization**: 40% better than Q4_K_S/Q5_K_S

### Model-Specific Critical Notes
- ⚠️ **Qwen3**: Temperature >= 0.6 (NEVER 0) - causes endless repetitions
- ⚠️ **Reasoning Models**: NO "think step-by-step" prompts
- ⚠️ **Phi-4**: Requires `--jinja` flag
- ⚠️ **DeepSeek-R1**: NO system prompt support (user prompt only)
- ⚠️ **Gemma-3**: NO system prompt support (use CO-STAR framework)

### Min-P Sampling (ICLR 2025)
- **Breakthrough**: Dynamic truncation based on model confidence
- **Advantage**: Preserves coherence at high temperatures where top-p fails
- **Recommended**: `min_p=0.05` to `0.1` with `temp=1.0-1.2`
- **Adoption**: Hugging Face, vLLM, llama.cpp all support

---

## 🎯 Optimal Commands (2025)

### Standard Inference
```bash
wsl bash -c "~/llama.cpp/build/bin/llama-cli \
  -m /mnt/d/models/organized/model.gguf \
  -p 'your prompt here' \
  -ngl 999 \
  -t 24 \
  -b 512 \
  -ub 512 \
  -fa 1 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --no-ppl \
  --temp 0.7 \
  --top-p 0.9 \
  --top-k 40 \
  --mlock"
```

### Qwen3 Models (with thinking mode)
```bash
wsl bash -c "~/llama.cpp/build/bin/llama-cli \
  -m /mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf \
  -p 'your prompt' \
  -ngl 999 \
  -t 24 \
  -b 512 \
  -fa 1 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --no-ppl \
  --temp 0.7 \
  --top-p 0.8 \
  --top-k 20 \
  --jinja \
  --mlock"
```

### Phi-4 Reasoning
```bash
wsl bash -c "~/llama.cpp/build/bin/llama-cli \
  -m /mnt/d/models/organized/microsoft_Phi-4-reasoning-plus-Q6_K.gguf \
  -p 'direct goal here' \
  -ngl 999 \
  -t 24 \
  -b 512 \
  -fa 1 \
  --no-ppl \
  --temp 0.7 \
  --jinja \
  --mlock"
```

### Automated PowerShell (Easiest)
```powershell
# Run any model with optimal settings
.\RUN-MODEL-WITH-PROMPT.ps1 -Model Qwen3Coder -UserPrompt "Write a Python async web scraper" -UseOptimalContext

# Available models:
# RTX 3090: Llama70B, Qwen3Coder, DolphinVenice, Phi4, Gemma3, Ministral3, DeepSeekR1, WizardVicuna, Dolphin8B
# RTX 4060 Ti: Qwen14BInstruct, Qwen14BUncensored, Llama8B, QwenCoder7B
```

---

## 📊 Expected Performance (RTX 3090 24GB)

| Model | Tokens/Second |
|-------|---------------|
| Llama 70B IQ2_S | 20-35 tok/sec |
| Qwen3-Coder-30B Q4_K_M | 25-40 tok/sec |
| Phi-4-Reasoning-Plus Q6_K | 35-55 tok/sec |
| Ministral-3-14B Q5_K_M | 40-60 tok/sec |
| DeepSeek-R1-Distill Q5_K_M | 25-35 tok/sec (reasoning) |
| Gemma-3-27B Q2_K | 25-40 tok/sec |
| Dolphin-Mistral-24B Q4_K_M | 30-50 tok/sec |
| Dolphin-3.0-8B Q6_K | 60-90 tok/sec |

**Target GPU Utilization**: 80-100%

---

## ⚙️ WSL Configuration (.wslconfig)

Location: `%UserProfile%\.wslconfig`

```ini
[wsl2]
# Memory - 75% of total RAM
memory=48GB

# CPU cores - leave 1-2 for Windows
processors=22

# Large swap for LLM workloads (2-3x memory)
swap=96GB
swapFile=C:\\wsl-swap.vhdx

# Memory management
pageReporting=true

# GPU support
nestedVirtualization=true
vmIdleTimeout=-1

[experimental]
# Gradual memory reclaim after 5min idle
autoMemoryReclaim=gradual

# Auto-shrinking VHDs
sparseVhd=true

# Network optimizations
dnsTunneling=true
networkingMode=mirrored
firewall=true
```

**After changes**: Run `wsl --shutdown` then restart WSL

### WSL Requirements
**Windows Side:**
- NVIDIA Driver >= 528.33
- Windows 11 recommended

**WSL Side:**
```bash
# Install CUDA toolkit only (NOT drivers)
sudo apt install cuda-toolkit-12-6

# Verify GPU access
nvidia-smi

# For large model workloads
export NIM_RELAX_MEM_CONSTRAINTS=1
```

⚠️ **Critical**: Do NOT install `cuda-drivers` package in WSL - conflicts with Windows driver stub

---

## 🎓 Quick Parameter Guide

### Temperature by Task
| Task Type | Temperature | Notes |
|-----------|-------------|-------|
| Code generation | 0.1-0.3 | Precision required |
| Math/reasoning | 0.2-0.7 | Balance creativity & accuracy |
| General chat | 0.6-0.8 | Natural conversation |
| Creative writing | 0.8-1.2 | Maximum creativity |
| Structured JSON | 0.0 | Deterministic output |

### Sampling Recommendations
- **General purpose**: `temp=0.7, top_p=0.9, top_k=40`
- **Creative with min-p**: `temp=1.2, min_p=0.08, top_p=0.9`
- **Precise factual**: `temp=0.3, top_p=0.85, top_k=20`
- **Reasoning models**: Use `reasoning_effort` parameter, NOT temperature

---

## ❌ Common Mistakes to Avoid (2025)

1. ❌ Using Windows Ollama or Windows llama.cpp (WSL matches/exceeds performance)
2. ❌ Not using `-ngl 999` (miss full GPU acceleration)
3. ❌ Using greedy decoding (`temp=0`) with Qwen models (causes endless repetitions)
4. ❌ Not using `--jinja` flag with Phi-4 (disables reasoning format)
5. ❌ Using "think step-by-step" with reasoning models (degrades performance)
6. ❌ Setting batch size below 512 (suboptimal memory usage)
7. ❌ Not enabling Flash Attention on CUDA GPUs (miss 1.2x speedup)
8. ❌ Not using KV cache quantization for long contexts (miss 50% memory savings)
9. ❌ Installing `cuda-drivers` in WSL (conflicts with Windows driver stub)
10. ❌ Not allocating enough swap in WSL for LLM workloads (causes OOM)

---

## 📖 Research Sources (Sep-Nov 2025)

- llama.cpp GitHub releases
- NVIDIA: Leveling up CUDA Performance on WSL2
- NVIDIA: Optimizing llama.cpp with CUDA Graphs
- Min-P Sampling (ICLR 2025 - OpenReview)
- Qwen3 Official Documentation (QwenLM GitHub)
- DeepSeek-R1 Technical Report (Nature, arXiv)
- Phi-4 Technical Report (Microsoft Research)
- AMD ROCm Blog: llama.cpp Meets Instinct
- Quantization Hurts Reasoning? (COLM 2025)
- The Prompt Report: Systematic Survey (Feb 2025)
- Context Engineering is the New Prompt Engineering (2025)
- vLLM Structured Decoding (Jan 2025)
- Community benchmarks (r/LocalLLaMA, Sep-Nov 2025)

---

## 🔍 Validation Checklist

Before running inference, verify:
- [ ] Using WSL (within 1% of native Linux)
- [ ] `-ngl 999` in command (full GPU offload)
- [ ] `-t 24` in command (all CPU threads)
- [ ] `-b 512` minimum (optimal: 512-2048)
- [ ] `-ub 512` (logical batch size)
- [ ] `-fa 1` (Flash Attention for CUDA)
- [ ] `--cache-type-k q8_0 --cache-type-v q8_0` (for long contexts)
- [ ] `--no-ppl` in command (+15% speedup)
- [ ] Model-specific flags: `--jinja` for Qwen3/Phi-4
- [ ] Qwen models: temperature >= 0.6
- [ ] Reasoning models: minimal prompts, no CoT instructions
- [ ] WSL memory: 75% of total RAM, swap 2-3x memory
- [ ] NVIDIA driver >= 528.33 on Windows
- [ ] Only `cuda-toolkit` installed in WSL, NO `cuda-drivers`

---

## 🎉 Setup Complete!

All models downloaded, documented, and optimized with 2025 research best practices.

**Next Steps:**
1. Test models with `RUN-MODEL-WITH-PROMPT.ps1`
2. Monitor performance with `MONITOR-PERFORMANCE.ps1`
3. Validate configuration with `VALIDATE-CONFIG.ps1`
4. Read system prompts in individual `.txt` files

**For help:** See `SYSTEM-PROMPTS-QUICK-START.md` or `2025-RESEARCH-SUMMARY.md`
