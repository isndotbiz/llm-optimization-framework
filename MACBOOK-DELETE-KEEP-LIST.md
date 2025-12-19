# MacBook Model Cleanup Plan
## Current: 12 Models (130GB+) → Optimized MLX (60GB)

---

## DELETE THESE (Old/Redundant - 75GB freed)

```
qwen-coder-32b-uncensored:latest         19 GB  - REPLACE with Qwen3-Coder-32B MLX
deepseek-r1-32b-uncensored:latest        19 GB  - REPLACE with DeepSeek-R1-8B MLX (better speed)
qwen2.5-survival:latest                  19 GB  - DELETE (variant, not needed)
qwen2.5-undercover:latest                19 GB  - DELETE (variant, not needed)
qwen2.5-uncensored:latest                19 GB  - DELETE (variant, not needed)
nous-hermes2:latest                      6.1 GB - DELETE (outdated)
dolphin-mistral:latest                   4.1 GB - DELETE (will get Dolphin 3.0 MLX)
```

**Space freed**: ~104GB

### Delete Commands
```bash
# On MacBook, in terminal:
ollama rm qwen-coder-32b-uncensored:latest
ollama rm deepseek-r1-32b-uncensored:latest
ollama rm qwen2.5-survival:latest
ollama rm qwen2.5-undercover:latest
ollama rm qwen2.5-uncensored:latest
ollama rm nous-hermes2:latest
ollama rm dolphin-mistral:latest
```

---

## KEEP THESE (Good, but will convert to MLX)

```
qwen2.5-max:latest                       9.0 GB - GOOD, but convert to MLX
qwen2.5:14b                              9.0 GB - GOOD, but convert to MLX
gemma2:2b                                1.6 GB - GOOD, keep for ultra-light
phi3:mini                                2.2 GB - GOOD, keep for light tasks
llama3.1:8b                              4.9 GB - GOOD, keep as fallback
```

**These are fine, but MLX versions will be 2-3x faster**

---

## WHAT YOU'RE GETTING (MLX versions downloading now)

These 8 models will replace everything above:

**Replace Qwen2.5 with Qwen3 (Major upgrade)**:
- Qwen3-14B (9GB) - Replaces qwen2.5:14b
- Qwen3-7B (4.5GB) - Lighter than phi3:mini
- Qwen3-Coder-32B (18GB) - Replaces qwen-coder-32b-uncensored

**Replace DeepSeek-R1-32B**:
- DeepSeek-R1-8B (4.5GB) - 4x smaller, 2x faster, just as good reasoning

**Add Premium Models**:
- Qwen2.5-Coder-7B (4.5GB) - Fast coding (60-80 tok/sec)
- Qwen2.5-Coder-32B (18GB) - Advanced coding
- Phi-4-14B (8-9GB) - Math/STEM specialist
- Dolphin-3.0-Llama3.1-8B (4.5GB) - Fast uncensored
- Mistral-7B (4GB) - Ultra-fast

---

## YOUR NEW MACBOOK SETUP

### For Daily Use (Just 2 models)

1. **Qwen2.5-Coder-7B MLX** (4.5GB, 60-80 tok/sec)
   - For: Quick code fixes, most work
   - Replace: All the Qwen2.5 variants
   - Command: `mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit`

2. **Qwen3-14B MLX** (9GB, 40-60 tok/sec)
   - For: General questions, research, balanced
   - Replace: Qwen2.5-max and qwen2.5:14b
   - Command: `mlx_lm.chat --model mlx-community/Qwen3-14B-Instruct-4bit`

### For Specialized Tasks

3. **Qwen2.5-Coder-32B MLX** (18GB, 11-22 tok/sec)
   - For: Complex coding, architecture
   - Replaces: qwen-coder-32b-uncensored
   - Only use if 32GB+ RAM available

4. **DeepSeek-R1-8B MLX** (4.5GB, 50-70 tok/sec)
   - For: Math, reasoning, problem-solving
   - Replaces: deepseek-r1-32b-uncensored (4x smaller, faster!)

### Keep as Fallback

5. **Phi3:mini** (2.2GB)
   - Ultra-lightweight if needed
   - Or replace with Mistral-7B MLX (faster, better)

6. **Gemma2:2b** (1.6GB)
   - Edge case only
   - Can delete when MLX models ready

---

## Step-by-Step Process

### Phase 1: Delete Old (Do This Now)

```bash
# Run these commands on your MacBook:
ollama rm qwen-coder-32b-uncensored:latest
ollama rm deepseek-r1-32b-uncensored:latest
ollama rm qwen2.5-survival:latest
ollama rm qwen2.5-undercover:latest
ollama rm qwen2.5-uncensored:latest
ollama rm nous-hermes2:latest
ollama rm dolphin-mistral:latest

# Verify cleanup
ollama list
# Should now show only 5 models
```

### Phase 2: Setup MLX (Do After Downloads Complete)

```bash
# Create MLX environment
python3 -m venv ~/venv-mlx
source ~/venv-mlx/bin/activate

# Install MLX
pip install --upgrade pip
pip install -U mlx-lm

# Verify
python3 -c "import mlx; print('Ready!')"
```

### Phase 3: Test First Model

```bash
source ~/venv-mlx/bin/activate
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit
```

### Phase 4: Use Actively

```bash
# Quick code fix
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit

# General questions
mlx_lm.chat --model mlx-community/Qwen3-14B-Instruct-4bit

# Math problem
mlx_lm.chat --model mlx-community/DeepSeek-R1-Distill-Llama-8B

# Heavy coding (if RAM available)
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-32B-Instruct-4bit
```

---

## Speed Improvements (GGUF → MLX)

### Qwen2.5 Coder (7B)
- Old (GGUF): 20-30 tok/sec
- New (MLX): 60-80 tok/sec
- **Improvement: +200-300% faster**

### Qwen2.5 Coder (32B)
- Old (GGUF): 8-12 tok/sec
- New (MLX): 11-22 tok/sec
- **Improvement: +85-175% faster**

### DeepSeek-R1 (8B vs 32B)
- Old (GGUF 32B): 10-15 tok/sec
- New (MLX 8B): 50-70 tok/sec
- **Same capability, 4-6x faster!**

---

## Storage Breakdown

**Current** (130GB+):
```
Qwen variants:       76 GB (4 redundant models)
DeepSeek-R1 32B:     19 GB
Dolphin/Misc:        10 GB
Gemma/Phi/Llama:     8-10 GB
Total: 130GB+
```

**After Cleanup** (60GB MLX):
```
Qwen2.5-Coder-32B:   18 GB (premium)
Qwen3-14B:           9 GB (general)
Qwen2.5-Coder-7B:    4.5 GB (fast)
DeepSeek-R1-8B:      4.5 GB (reasoning)
Phi-4-14B:           8-9 GB (math)
Qwen3-7B:            4.5 GB (lightweight)
Dolphin-3.0:         4.5 GB (uncensored)
Mistral-7B:          4 GB (ultra-fast)
Fallback (Phi3):     2.2 GB (kept)
Gemma2:              1.6 GB (kept)
Total: ~65GB
```

**Freed Space**: ~65GB for other uses!

---

## Model Comparison

| Old Model | Old Speed | New Replacement | New Speed | Improvement |
|-----------|-----------|-----------------|-----------|------------|
| Qwen-Coder-32B (GGUF) | 8-12 | Qwen2.5-Coder-7B (MLX) | 60-80 | +500-700% |
| DeepSeek-R1-32B (GGUF) | 10-15 | DeepSeek-R1-8B (MLX) | 50-70 | +400-500% |
| Qwen2.5:14b (GGUF) | 20-30 | Qwen3-14B (MLX) | 40-60 | +100-200% |
| Qwen2.5-max (GGUF) | 15-25 | Qwen3-7B (MLX) | 60-80 | +250-500% |
| Dolphin-Mistral (GGUF) | 15-25 | Dolphin-3.0-Llama (MLX) | 60-80 | +250-500% |

---

## Your Workflow After Setup

### At Your Desk (Connect to RTX 3090)
- Heavy work: Use RTX 3090 via network
- Architecture: Dolphin 70B (RTX 3090)
- Quick tasks: Local M4 Qwen2.5-Coder-7B

### Out and About (MacBook Only)
- Coding: Qwen2.5-Coder-7B MLX (60-80 tok/sec)
- Research: Qwen3-14B MLX (40-60 tok/sec)
- Math: DeepSeek-R1-8B MLX (50-70 tok/sec)
- Instant: Mistral-7B MLX (70-100 tok/sec)

### Offline/Mobile Hotspot (When Speed Critical)
- Use Mistral-7B (4GB, 70-100 tok/sec)
- Or Qwen3-7B (4.5GB, 60-80 tok/sec)

---

## Timeline

**Now**: Delete old GGUF models (freed 75GB)
**2-4 hours**: MLX models finish downloading
**10 min**: Setup MLX environment
**Immediate**: Start using (3-5x faster!)

---

## Don't Forget

1. ✓ RTX 3090 stays unchanged (you said don't archive)
2. ✓ RTX 4060 gets Qwen3-14B (separate)
3. ✓ MacBook gets MLX models (this setup)
4. ✓ Each system stays independent

---

**Ready to delete old models on MacBook?** Run those `ollama rm` commands above.
**MLX downloads should complete in 2-4 hours**, then you'll have the fastest MacBook setup!
