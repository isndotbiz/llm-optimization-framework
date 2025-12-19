#!/bin/bash
# MacBook MLX Model Downloader
# Run this on your M4 MacBook Pro
# Usage: bash download-macbook-mlx.sh

set -e

echo "========================================================================"
echo "MACBOOK MLX MODEL DOWNLOADER"
echo "========================================================================"

# Create directories
mkdir -p ~/models/mlx

# Install huggingface_hub if needed
echo "Checking huggingface_hub installation..."
python3 -c "import huggingface_hub" 2>/dev/null || pip install huggingface-hub

echo ""
echo "Starting MLX model downloads to ~/models/mlx/"
echo ""

# Array of models to download
models=(
    "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit:qwen25-coder-7b"
    "mlx-community/Qwen2.5-Coder-32B-Instruct-4bit:qwen25-coder-32b"
    "mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit:qwen3-coder-30b"
    "mlx-community/Qwen3-14B-Instruct-4bit:qwen3-14b"
    "mlx-community/Qwen3-7B-Instruct-4bit:qwen3-7b"
    "mlx-community/DeepSeek-R1-Distill-Llama-8B:deepseek-r1-8b"
    "mlx-community/phi-4-4bit:phi-4"
    "mlx-community/Dolphin3.0-Llama3.1-8B:dolphin-llama3.1-8b"
    "mlx-community/Mistral-7B-Instruct-v0.3-4bit:mistral-7b"
)

total=${#models[@]}
completed=0
failed=0

for i in "${!models[@]}"; do
    IFS=':' read -r repo_id local_name <<< "${models[$i]}"
    index=$((i + 1))

    echo "[$index/$total] Downloading: $local_name"
    echo "    From: $repo_id"
    echo "    To: ~/models/mlx/$local_name"

    if python3 -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='$repo_id',
    local_dir=os.path.expanduser('~/models/mlx/$local_name'),
    local_dir_use_symlinks=False,
)
" 2>/dev/null; then
        echo "    SUCCESS"
        ((completed++))
    else
        echo "    FAILED - Retrying with direct command..."
        if huggingface-cli download "$repo_id" --local-dir ~/models/mlx/$local_name 2>/dev/null; then
            echo "    SUCCESS (retry)"
            ((completed++))
        else
            echo "    FAILED"
            ((failed++))
        fi
    fi
    echo ""
done

echo "========================================================================"
echo "DOWNLOAD COMPLETE"
echo "Successful: $completed/$total"
echo "Failed: $failed/$total"
echo "Location: ~/models/mlx/"
echo "========================================================================"

echo ""
echo "To use your models:"
echo "  source ~/venv-mlx/bin/activate"
echo "  mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit"
