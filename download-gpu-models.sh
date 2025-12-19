#!/bin/bash
# GPU Server Model Downloader
# Run this on RTX 3090 or RTX 4060 Ti Windows machine
# Usage: bash download-gpu-models.sh

set -e

echo "========================================================================"
echo "GPU SERVER MODEL DOWNLOADER (RTX 3090 + RTX 4060)"
echo "========================================================================"

# Create directories
mkdir -p /d/models/organized

# Install huggingface_hub if needed
echo "Checking huggingface_hub installation..."
python3 -c "import huggingface_hub" 2>/dev/null || pip install huggingface-hub

echo ""
echo "Starting GPU model downloads to /d/models/organized/"
echo ""

# Array of models to download
models=(
    "bartowski/dolphin-2.9.1-llama-3-70b-GGUF:dolphin-2.9.1-llama-3-70b"
    "cognitivecomputations/Dolphin3.0-R1-Mistral-24B:dolphin-r1-mistral-24b"
    "Qwen/Qwen3-14B-Instruct-GGUF:qwen3-14b"
)

total=${#models[@]}
completed=0
failed=0

for i in "${!models[@]}"; do
    IFS=':' read -r repo_id local_name <<< "${models[$i]}"
    index=$((i + 1))

    echo "[$index/$total] Downloading: $local_name"
    echo "    From: $repo_id"
    echo "    To: /d/models/organized/$local_name"

    if python3 -c "
from huggingface_hub import snapshot_download
import os
snapshot_download(
    repo_id='$repo_id',
    local_dir='/d/models/organized/$local_name',
    local_dir_use_symlinks=False,
)
" 2>/dev/null; then
        echo "    SUCCESS"
        ((completed++))
    else
        echo "    FAILED - Retrying with direct command..."
        if huggingface-cli download "$repo_id" --local-dir /d/models/organized/$local_name 2>/dev/null; then
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
echo "Location: /d/models/organized/"
echo "========================================================================"

echo ""
echo "RTX 3090 Models:"
echo "  - Dolphin 2.9.1 Llama 3 70B (21GB)"
echo "  - Dolphin 3.0 R1 Mistral 24B (15GB)"
echo ""
echo "RTX 4060 Ti Models:"
echo "  - Qwen3 14B (8-10GB)"
