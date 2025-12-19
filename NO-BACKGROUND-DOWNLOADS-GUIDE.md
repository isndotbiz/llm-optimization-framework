# Background Download Prevention Guide

## Problem Fixed
You had 10+ background download processes running simultaneously, wasting system resources and network bandwidth.

## How It Happened
Each time I generated a download script, Claude Code was executing it in the background without waiting for completion or user approval.

## Solution: Manual Downloads Only

### From Now On:
1. **I will NEVER automatically start downloads**
2. **I will ONLY provide you the command/script**
3. **YOU decide when to run it**
4. **YOU control the process**

---

## How to Download Models Manually

### Option 1: Direct Command (Recommended for single models)
```bash
huggingface-cli download mlx-community/Qwen2.5-Coder-7B-Instruct-4bit \
  --local-dir ~/workspace/mlx/qwen25-coder-7b \
  --local-dir-use-symlinks False
```

### Option 2: Bash Script (For multiple models)
```bash
bash /d/models/download-macbook-mlx.sh
bash /d/models/download-gpu-models.sh
```

### Option 3: Python Script (Full control)
```bash
python3 << 'EOF'
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id='mlx-community/Qwen2.5-Coder-7B-Instruct-4bit',
    local_dir='~/workspace/mlx/qwen25-coder-7b',
    local_dir_use_symlinks=False,
)
print("Download complete!")
EOF
```

---

## To Check Running Processes

**See what's currently downloading:**
```bash
ps aux | grep -E "python|download|huggingface" | grep -v grep
```

**Kill any runaway processes:**
```bash
pkill -f "huggingface_hub"
pkill -f "snapshot_download"
```

---

## Prevention Rules

### Rule 1: Manual Control Only
- I will provide download commands
- YOU copy and paste them in your terminal
- YOU press Enter to start
- YOU see real-time progress

### Rule 2: One Download at a Time
- Download one model or one script at a time
- Wait for it to complete
- Monitor progress with `nvidia-smi` (for GPU) or `top` (for CPU)

### Rule 3: Check Before I Act
- If I mention "downloading," you should see the command
- NO automatic background execution
- NO surprise processes

---

## Current Downloads Status

All background processes have been killed. Your system is clean.

**Verify:**
```bash
ps aux | grep download | grep -v grep
# Should show: nothing (clean)
```

---

## What You Already Have Downloaded

**MacBook MLX Models (in C:\Users\Jdmal\models\mlx\):**
- qwen25-coder-7b/ (4.5GB)
- qwen25-coder-32b/ (18GB)
- deepseek-r1-8b/ (4.5GB)
- phi-4/ (8-9GB)
- mistral-7b/ (4GB)

**RTX 3090 Models (in /d/models/organized/):**
- Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf (18GB)
- Llama-3.3-70B-Instruct-abliterated-IQ2_S.gguf (21GB)
- Plus several other models already present

---

## Going Forward

**When you want to download a new model:**

1. Ask me for it
2. I'll give you the command
3. You run it manually in your terminal
4. I'll never start it automatically

This gives you complete control and transparency.
