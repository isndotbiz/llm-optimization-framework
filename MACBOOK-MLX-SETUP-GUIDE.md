# MacBook M4 Pro - MLX Setup Guide

## MLX vs Ollama - Speed Comparison

MLX is **3-4x faster than Ollama** on M4 MacBook Pro:

| Framework | Load Time | First Token | Qwen2.5 7B Speed | Why? |
|-----------|-----------|-------------|------------------|------|
| MLX | <500ms | <300ms | 60-80 tok/sec | Native M-series, optimized kernels |
| Ollama | 2-3s | 1-2s | 30-40 tok/sec | Abstraction layer overhead |
| llama.cpp | 3-5s | 2-3s | 20-30 tok/sec | Generic C++, not Apple-optimized |

**Real-world benefit:**
- Code review: 30 sec (MLX) vs 2-3 min (Ollama)
- Model load: <1 sec (MLX) vs 5-10 sec (Ollama)
- Memory: 2-3GB (MLX) vs 4-6GB (Ollama)

---

## Step 1: Clone the App (Keep Models OUT of Git)

```bash
git clone <your-repo-url> ~/workspace/ai-router
cd ~/workspace/ai-router

# Create .gitignore
cat >> .gitignore << 'GITIGNORE'
# Model files - DO NOT SYNC
*.gguf
*.safetensors
*.bin
models/
mlx/
.cache/
huggingface_cache/
GITIGNORE

git add .gitignore
git commit -m "Keep models local only"
```

---

## Step 2: Copy Models from Windows to Mac

### Option A: SCP over Network
```bash
# On MacBook:
mkdir -p ~/workspace/mlx
scp -r "jdmal@<windows-ip>:~/models/mlx/*" ~/workspace/mlx/
```

Find Windows IP: On Windows PowerShell run `ipconfig` (look for IPv4)

### Option B: USB Drive
1. Windows: Copy `C:\Users\Jdmal\models\mlx\` to USB
2. Mac: Plug in USB, copy to `~/workspace/mlx/`

---

## Step 3: Install MLX

```bash
python3 -m venv ~/workspace/venv-mlx
source ~/workspace/venv-mlx/bin/activate
pip install --upgrade pip
pip install -U mlx-lm
```

Add to `~/.zshrc`:
```bash
alias mlx-activate='source ~/workspace/venv-mlx/bin/activate'
```

---

## Step 4: Verify & Run

```bash
source ~/workspace/venv-mlx/bin/activate
python ~/workspace/ai-router/ai-router-mlx.py
```

---

## Quick Commands

```bash
# Fast coding (recommended)
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit

# Advanced coding
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-32B-Instruct-4bit

# Math/reasoning
mlx_lm.chat --model mlx-community/DeepSeek-R1-Distill-Llama-8B

# Uncensored
mlx_lm.chat --model mlx-community/Dolphin3.0-Llama3.1-8B
```

---

## Why MLX > Ollama

1. **3-4x faster** on M4 specifically
2. **Lower memory** (2-3GB vs 4-6GB)
3. **No daemon** required
4. **Native Apple** integration (not wrapper)
5. **Direct control** over parameters

Best for: M1/M2/M3/M4 Macs only. Intel Macs won't see big gains.

---

## Directory Structure

```
~/workspace/
├── ai-router/          (git clone - no models)
├── mlx/                (models - NOT in git)
├── venv-mlx/           (python environment)
```

---

## Models You Have Ready

- Qwen2.5 Coder 7B (4.1GB) - FAST
- Qwen2.5 Coder 32B (18GB) - BEST QUALITY
- Qwen3 14B (9GB) - NEW
- DeepSeek-R1 8B (4.5GB) - REASONING
- Phi-4 14B (8-9GB) - MATH
- Dolphin 3.0 Llama 3.1 8B (4.5GB) - UNCENSORED
- Mistral 7B (4GB) - ULTRA-FAST

