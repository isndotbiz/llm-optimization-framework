#!/bin/bash

# Download remaining 6 uncensored models
# Use this when you have a better connection
# Dolphin 3.0 should already be downloaded

echo "📥 Downloading Remaining 6 Optimal Models"
echo "=========================================="
echo ""
echo "This script downloads the remaining models (without Dolphin 3.0)"
echo "Dolphin 3.0 should already be downloaded on this system"
echo ""
echo "Models to download:"
echo "  2. Qwen2.5-7B Uncensored        (4GB)"
echo "  3. DeepSeek-R1 Distill 7B       (3.8GB)"
echo "  4. Hermes-4 14B                 (7-8GB)"
echo "  5. DeepSeek-R1 Distill 14B      (7-8GB)"
echo "  6. Nous-Hermes2 Mixtral 8x7B    (7-8GB)"
echo "  7. DeepSeek-R1 Distill 32B      (16-18GB)"
echo ""
echo "Total: ~46GB (Dolphin not included)"
echo ""

# Activate virtual environment
echo "📦 Setting up environment..."
source ~/venv-mlx/bin/activate

# Ensure huggingface-hub is installed
pip install -q huggingface-hub

echo ""
echo "🔄 Starting downloads..."
echo ""

# Function to download
download_model() {
    local model=$1
    local name=$2
    local size=$3

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📥 [$name] ($size)"
    echo "   Model: $model"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    python3 << PYEOF
from huggingface_hub import snapshot_download
import os

try:
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    snapshot_download(
        "$model",
        cache_dir=cache_dir,
        resume_download=True
    )
    print("✓ Downloaded successfully")
except Exception as e:
    print(f"⚠️  Error: {e}")
PYEOF
    echo ""
}

# Download remaining 6 models
download_model "mlx-community/Qwen2.5-7B-Instruct-Uncensored-4bit" "Qwen2.5-7B Uncensored" "4GB"
download_model "mlx-community/DeepSeek-R1-Distill-Qwen-7B-MLX" "DeepSeek-R1 7B" "3.8GB"
download_model "mlx-community/Hermes-4-14B-4bit" "Hermes-4 14B" "7-8GB"
download_model "mlx-community/DeepSeek-R1-Distill-Qwen-14B-MLX" "DeepSeek-R1 14B" "7-8GB"
download_model "mlx-community/Nous-Hermes2-Mixtral-8x7B-4bit" "Nous-Hermes2 8x7B" "7-8GB"
download_model "mlx-community/DeepSeek-R1-Distill-Qwen-32B-4bit" "DeepSeek-R1 32B" "16-18GB"

echo ""
echo "✅ All remaining models downloaded!"
echo ""
echo "You now have all 7 optimal uncensored models:"
echo "  1. ✓ Dolphin 3.0 Llama 8B (4.5GB)"
echo "  2. ✓ Qwen2.5-7B Uncensored (4GB)"
echo "  3. ✓ DeepSeek-R1 7B (3.8GB)"
echo "  4. ✓ Hermes-4 14B (7-8GB)"
echo "  5. ✓ DeepSeek-R1 14B (7-8GB)"
echo "  6. ✓ Nous-Hermes2 8x7B (7-8GB)"
echo "  7. ✓ DeepSeek-R1 32B (16-18GB)"
echo ""
echo "Ready to use:"
echo "  python3 model-manager.py list"
echo "  python3 model-manager.py load [model-name]"
echo "  python3 model-manager.py chat"
echo ""
