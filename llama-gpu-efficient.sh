#!/bin/bash
# Efficient llama.cpp wrapper for RTX 3090
# Prevents unnecessary RAM binding by using smart GPU offloading
# Usage: ./llama-gpu-efficient.sh <model_path> "<prompt>"

set -e

MODEL_PATH="${1:-/mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf}"
PROMPT="${2:-What is the best way to optimize code?}"
CONTEXT_SIZE="${3:-32768}"

# Verify model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "[ERROR] Model not found: $MODEL_PATH"
    exit 1
fi

echo "========================================"
echo "EFFICIENT GPU INFERENCE - RTX 3090"
echo "========================================"
echo "Model: $MODEL_PATH"
echo "Prompt: $PROMPT"
echo ""

# KEY FLAGS FOR MEMORY EFFICIENCY:
# -ngl 80      = Offload 80 layers to GPU (RTX 3090 can handle ALL)
# -b 1024      = LARGER batch size = LESS RAM usage (counterintuitive!)
# -ub 1024     = Larger ubatch = better GPU utilization
# -fa 1        = Flash attention = 50% memory reduction
# --cache-type-k q8_0 = Quantize KV cache (saves 8GB+ RAM)
# --no-mmap    = DON'T memory-map file (prevents RAM binding)
# --mlock      = Lock model in GPU VRAM (doesn't use RAM)

echo "[*] Launching llama.cpp with GPU optimization..."
echo "[*] Using Q4_K_M quantization"
echo "[*] Memory policy: GPU-first, minimal RAM binding"
echo ""

# Run with optimized parameters
~/llama.cpp/build/bin/llama-cli \
  -m "$MODEL_PATH" \
  -p "$PROMPT" \
  -n 512 \
  -ngl 80 \
  -t 24 \
  -b 1024 \
  -ub 1024 \
  -fa 1 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --temp 0.7 \
  --top-p 0.9 \
  --top-k 40 \
  -c "$CONTEXT_SIZE" \
  --no-mmap \
  --mlock

echo ""
echo "[✓] Inference complete"
