#!/bin/bash

# Download all uncensored MLX models for your 24GB M4
# Models are loaded on-demand, not all at once

echo "🚀 MLX Model Downloader - Uncensored Models for 24GB M4"
echo "========================================================"
echo ""
echo "This will download:"
echo "  ✓ Dolphin 3.0 Llama 8B (4.5GB) - Best uncensored"
echo "  ✓ Hermes-4 14B (7-8GB) - Creative/unrestricted"
echo "  ✓ DeepSeek-R1 Distill 14B (7-8GB) - Reasoning"
echo "  ✓ DeepSeek-R1 Distill 32B (16-18GB) - Advanced"
echo "  ✓ Qwen2.5-7B Uncensored (4GB) - Fast"
echo ""
echo "Total: ~42-50GB (downloaded as needed, not loaded simultaneously)"
echo ""
echo "⏱️  Note: First download may take 30-60 minutes depending on internet speed"
echo ""

# Activate virtual environment
echo "📦 Activating virtual environment..."
source ~/venv-mlx/bin/activate

# Ensure huggingface-hub is installed
echo "📥 Ensuring huggingface-hub is installed..."
pip install -q huggingface-hub

echo ""
echo "Starting downloads..."
echo ""

# Array of models to download
declare -a models=(
    "mlx-community/Dolphin3.0-Llama3.1-8B-4bit"
    "mlx-community/Hermes-4-14B-4bit"
    "mlx-community/DeepSeek-R1-Distill-Qwen-14B-MLX"
    "mlx-community/DeepSeek-R1-Distill-Qwen-32B-4bit"
    "mlx-community/Qwen2.5-7B-Instruct-Uncensored-4bit"
)

# Download each model
for model in "${models[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📥 Downloading: $model"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    huggingface-cli download "$model" --cache-dir ~/.cache/huggingface/hub

    if [ $? -eq 0 ]; then
        echo "✓ Downloaded successfully"
    else
        echo "❌ Failed to download $model"
    fi
    echo ""
done

echo ""
echo "✅ Download complete!"
echo ""
echo "Next steps:"
echo "  1. Start the MLX server: source ~/venv-mlx/bin/activate && python3 mlx-server.py"
echo "  2. Use model manager: python3 model-manager.py list"
echo "  3. Load a model: python3 model-manager.py load dolphin-3.0"
echo "  4. Chat: python3 model-manager.py chat"
echo ""
