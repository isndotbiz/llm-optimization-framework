# AI Model Deployment Guide - 2025-12-16
## Complete Strategy for 3-Hardware Setup

**Status**: Downloads in progress
- GPU Models (RTX 3090 + RTX 4060): Downloading
- MLX Models (M4 MacBook Pro): Downloading

---

## Executive Summary

This guide provides a complete optimization strategy for your three-hardware AI system:

1. **RTX 3090 (24GB VRAM)** - Premium GPU Server
2. **RTX 4060 (16GB VRAM)** - Secondary GPU Server
3. **M4 MacBook Pro** - Local MLX-Optimized Development

**Key Strategy Changes:**
- **RTX 3090**: Upgrade from Qwen 2.5 to bleeding-edge Dolphin 2.9.1 70B + Qwen3 models
- **RTX 4060**: New setup with Qwen3-14B optimized for 16GB constraints
- **M4 MacBook**: Shift to MLX framework for 2-3x performance improvement over GGUF

---

## Hardware Configuration Recommendations

### 1. RTX 3090 (24GB VRAM) - Primary Workhorse

**Current Setup Issues:**
- Qwen2.5 variants are good but pre-Qwen3 architecture
- Dolphin-Mistral 24B is older Dolphin 2.x generation
- Room for significant upgrades

**Recommended New Models:**

#### Tier 1: Supreme Coding (Default)
**Dolphin 2.9.1 Llama 3 70B Q4_K_M** (21GB)
- **Performance**: 15-25 tok/sec, 128K context
- **Use**: Advanced coding, architecture design, complex debugging
- **Why Upgrade**: 70B vs 24B (3x parameters), better Llama 3.1 base, latest Dolphin 2.9.1 training
- **Model Path**: `/d/models/organized/dolphin-2.9.1-llama-3-70b/`

#### Tier 2: Reasoning + Coding (Secondary)
**Dolphin 3.0 R1 Mistral 24B Q4_K_M** (15GB)
- **Performance**: 25-35 tok/sec, 32K context
- **Use**: Coding with reasoning, math problems, agentic workflows
- **Why Upgrade**: R1 training (800k reasoning traces), Dolphin 3.0 generation
- **Model Path**: `/d/models/organized/dolphin-r1-mistral-24b/`

#### Tier 3: General Assistant (Fallback)
**Keep Qwen3-Coder-30B-A3B Q4_K_M** (18GB) ✓ Already Optimal
- **Performance**: 25-35 tok/sec, 32K context
- **Use**: Code generation, instruction following, balanced performance
- **Note**: Already at Qwen3 generation, no upgrade needed

**VRAM Budget**: Can run all 3 simultaneously (21+15+18=54GB) with layer offloading
**Recommended**: Primary + Secondary (21+15=36GB) or Primary + Tertiary (21+18=39GB)

**Models to Remove** (to free space):
- ❌ Llama-3.3-70B (redundant with Dolphin 2.9.1 70B)
- ❌ Dolphin-Mistral-24B-Venice (replaced by Dolphin 3.0 R1 24B)
- ❌ DeepSeek-R1-14B (covered by Dolphin models)
- ❌ Wizard-Vicuna-13B (outdated)

**Space Freed**: ~30GB

---

### 2. RTX 4060 (16GB VRAM) - Secondary Server

**Constraints**:
- Maximum model size: 14B (4-bit quantization)
- No layer offloading (keep responsive)
- Focus on speed + quality balance

**Recommended New Setup:**

#### Primary: General Purpose
**Qwen3-14B Q4_K_M** (8-10GB)
- **Performance**: 35-50 tok/sec, 128K context
- **Use**: General chat, instruction following, balanced tasks
- **Memory**: Leaves 6GB headroom for other processes
- **Model Path**: `/d/models/organized/qwen3-14b/`

**Alternative: Fast Inference**
**Qwen3-8B Q5_K_M** (6GB) - Faster but slightly lower quality

**Alternative: Specialized Coding**
**Qwen3-Coder-14B Q4_K_M** (8-10GB) - If pure coding focus

**Deployment Strategy**:
1. Primary use: Qwen3-14B (balanced)
2. Fallback: Qwen3-8B (if 4060 throttles)
3. Router decision: Auto-select based on task complexity

---

### 3. M4 MacBook Pro - Local Development with MLX

**Major Shift**: From GGUF → MLX Framework
- **2-3x faster** inference on Apple Silicon
- **Native M4 optimization** via Metal acceleration
- **128GB+ unified memory** support (if Pro/Max)

#### Configuration A: M4 Pro (24GB RAM)

**Primary: Fast Coding**
**Qwen2.5-Coder-7B MLX 4-bit** (4.5GB)
- **Performance**: 60-80 tok/sec
- **Use**: Quick code iterations, completions, fast debugging
- **Install**: `pip install mlx-lm && mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit`

**Secondary: Advanced Coding**
**Qwen2.5-Coder-32B MLX 4-bit** (18GB)
- **Performance**: 11-22 tok/sec
- **Use**: Architecture design, complex refactoring, thorough review
- **Caveat**: Leaves only 6GB free, monitor memory usage

**Alternative: Reasoning**
**DeepSeek-R1-Distill-8B MLX** (4.5GB)
- **Performance**: 50-70 tok/sec
- **Use**: Problem analysis, technical reasoning, research

#### Configuration B: M4 Max (64GB+ RAM)

**Tier 1: Fast Coding**
**Qwen2.5-Coder-7B MLX** (4.5GB) - Same as Pro

**Tier 2: Advanced Coding**
**Qwen2.5-Coder-32B MLX** (18GB) - Plenty of headroom

**Tier 3: Research/Complex**
**Qwen3-14B MLX 4-bit** (9GB) - General purpose reasoning

**All available**: Run multiple models simultaneously for parallel inference

#### Installation Instructions

```bash
# Create virtual environment
python3 -m venv ~/venv-mlx
source ~/venv-mlx/bin/activate

# Install MLX
pip install -U mlx-lm

# Run model interactively
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit

# Or Python API
python3 << 'EOF'
from mlx_lm import load, generate

model, tokenizer = load("mlx-community/Qwen2.5-Coder-7B-Instruct-4bit")
response = generate(
    model,
    tokenizer,
    prompt="Write a Python function to sort a list",
    max_tokens=500
)
print(response)
EOF
```

---

## Download Status

### Models Being Downloaded

#### GPU Models (for RTX 3090 + RTX 4060)
- [ ] Dolphin 2.9.1 Llama 3 70B (21GB)
- [ ] Dolphin 3.0 R1 Mistral 24B (15GB)
- [ ] Qwen3-14B for RTX 4060 (8-10GB)

#### MLX Models (for M4 MacBook Pro)
- [ ] Qwen2.5-Coder-7B MLX (4.5GB)
- [ ] Qwen2.5-Coder-32B MLX (18GB)
- [ ] DeepSeek-R1-Distill-8B MLX (4.5GB)
- [ ] Phi-4 14B MLX (8-9GB)
- [ ] Qwen3-14B MLX (9GB)

**Total Download Size**: ~110GB
**Estimated Time**: 3-6 hours (depends on internet speed)

---

## Configuration Updates Required

### 1. Update `ai-router-enhanced.py`

```python
# RTX 3090 Models - UPDATED
RTX3090_MODELS = {
    "dolphin-llama3-70b": {
        "name": "Dolphin 2.9.1 Llama 3 70B Q4_K_M",
        "path": "/d/models/organized/dolphin-2.9.1-llama-3-70b/*.gguf",
        "size": "21GB",
        "speed": "15-25 tok/sec",
        "use_case": "Advanced coding, architecture, complex debugging",
        "context": 131072,
        "framework": "llama.cpp"
    },
    "dolphin-r1-mistral-24b": {
        "name": "Dolphin 3.0 R1 Mistral 24B Q4_K_M",
        "path": "/d/models/organized/dolphin-r1-mistral-24b/*.gguf",
        "size": "15GB",
        "speed": "25-35 tok/sec",
        "use_case": "Coding with reasoning, math, agentic tasks",
        "context": 32768,
        "framework": "llama.cpp"
    },
    "qwen3-coder-30b": {
        "name": "Qwen3 Coder 30B MoE A3B Q4_K_M",
        "path": "/d/models/qwen3-coder-30b-a3b/*.gguf",
        "size": "18GB",
        "speed": "25-35 tok/sec",
        "use_case": "Code generation, instruction following",
        "context": 32768,
        "framework": "llama.cpp"
    }
}

# RTX 4060 Models - NEW
RTX4060_MODELS = {
    "qwen3-14b": {
        "name": "Qwen3 14B Q4_K_M",
        "path": "/d/models/organized/qwen3-14b/*.gguf",
        "size": "8-10GB",
        "speed": "35-50 tok/sec",
        "use_case": "General purpose, balanced performance",
        "context": 131072,
        "framework": "llama.cpp"
    }
}

# M4 MacBook Pro Models - NEW (MLX)
M4_MACBOOK_MODELS = {
    "qwen25-coder-7b-mlx": {
        "name": "Qwen2.5 Coder 7B MLX",
        "path": "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
        "size": "4.5GB",
        "speed": "60-80 tok/sec",
        "use_case": "Fast coding, completions",
        "context": 32768,
        "framework": "mlx"
    },
    "qwen25-coder-32b-mlx": {
        "name": "Qwen2.5 Coder 32B MLX",
        "path": "mlx-community/Qwen2.5-Coder-32B-Instruct-4bit",
        "size": "18GB",
        "speed": "11-22 tok/sec",
        "use_case": "Advanced coding, architecture",
        "context": 32768,
        "framework": "mlx"
    }
}
```

### 2. Create System Prompts

New files to create:
- `system-prompt-dolphin-llama3-70b.txt`
- `system-prompt-dolphin-r1-mistral-24b.txt`
- `system-prompt-qwen3-coder-30b.txt`
- `system-prompt-qwen3-14b.txt`
- `system-prompt-qwen25-coder-7b-mlx.txt`

---

## Implementation Timeline

### Phase 1: Download (In Progress)
- Downloads running in parallel
- ETA: 3-6 hours

### Phase 2: Archive Redundant Models (After Downloads)
```bash
mkdir -p /d/models/archive/removed-2025-12-16
# Move old models to archive
# Keep for 2 weeks before permanent deletion
```

### Phase 3: Configuration Update
- Update `ai-router-enhanced.py` with new models
- Create system prompts for each model
- Update router logic to select appropriate hardware

### Phase 4: Testing
- Test each model on respective hardware
- Benchmark performance
- Verify VRAM usage stays within limits

### Phase 5: Production Deployment
- Switch primary router to new configuration
- Monitor for any issues
- Permanent deletion of archived models (after 2 weeks)

---

## Expected Performance Gains

### RTX 3090
| Task | Old Setup | New Setup | Improvement |
|------|-----------|-----------|------------|
| Complex Coding | Qwen2.5 32B | Dolphin 70B | +40% quality, -40% speed |
| Code Review | Dolphin 24B | Dolphin 70B | +75% accuracy |
| Reasoning | DeepSeek-R1 | Dolphin R1 24B | +25% speed, same quality |

### RTX 4060
| Task | Old Setup | New Setup | Improvement |
|------|-----------|-----------|------------|
| General Chat | None | Qwen3-14B | New capability |
| Balanced Tasks | None | Qwen3-14B | New capability |
| Speed | N/A | 35-50 tok/sec | Good throughput |

### M4 MacBook Pro
| Task | Old Setup | New Setup | Improvement |
|------|-----------|-----------|------------|
| Fast Coding | GGUF 7B (20-30 tok/s) | MLX 7B (60-80 tok/s) | +150-170% speed |
| Advanced Code | GGUF 32B (5-10 tok/s) | MLX 32B (11-22 tok/s) | +55-120% speed |
| Developer UX | Slow iterations | Instant feedback | Major improvement |

---

## Quick Start Commands

### GPU Servers
```bash
# Start RTX 3090 with Dolphin 70B
ollama run dolphin-llama3-70b

# Start RTX 4060 with Qwen3-14B
ollama run qwen3:14b-q4
```

### M4 MacBook Pro
```bash
# Activate MLX environment
source ~/venv-mlx/bin/activate

# Fast coding (7B)
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit

# Advanced coding (32B)
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-32B-Instruct-4bit
```

---

## Next Steps (After Downloads Complete)

1. ✓ Downloads complete → Archive old models
2. ✓ Archive complete → Update configuration files
3. ✓ Configuration updated → Test each hardware setup
4. ✓ Testing complete → Update ai-router-enhanced.py
5. ✓ Router updated → Deploy to production

---

**Document Created**: 2025-12-16 07:10 UTC
**Downloads Started**: In progress (2 parallel processes)
**Estimated Completion**: 3-6 hours
