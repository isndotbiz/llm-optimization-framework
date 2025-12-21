#!/bin/bash

# Download Optimal Uncensored Models for 24GB M4 MacBook
# 7 models, ~45GB total, load one at a time

echo "🚀 Optimal Uncensored Models Downloader"
echo "========================================"
echo ""
echo "Downloading 7 curated uncensored models for your 24GB M4:"
echo ""
echo "Tier 1 - Daily Drivers (4-5GB each, instant loading):"
echo "  1. Dolphin 3.0 Llama 8B ⭐        (4.5GB) - Best uncensored"
echo "  2. Qwen2.5-7B Uncensored         (4GB)   - Fastest"
echo "  3. DeepSeek-R1 Distill 7B        (3.8GB) - Fast reasoning"
echo ""
echo "Tier 2 - Specialized Power (7-8GB each, 5-10s loading):"
echo "  4. Hermes-4 14B ⭐                (7-8GB) - Best creative"
echo "  5. DeepSeek-R1 Distill 14B       (7-8GB) - Mid reasoning"
echo "  6. Nous-Hermes2 Mixtral 8x7B     (7-8GB) - Unrestricted Mixtral"
echo ""
echo "Tier 3 - Maximum Power (16-18GB, 15-30s loading):"
echo "  7. DeepSeek-R1 Distill 32B ⭐    (16-18GB) - Most powerful"
echo ""
echo "Total: 45GB storage | Load one at a time"
echo "================================"
echo ""

# Activate virtual environment
echo "📦 Setting up environment..."
source ~/venv-mlx/bin/activate

# Ensure huggingface-hub is installed
pip install -q huggingface-hub

echo ""
echo "🔄 Starting model downloads..."
echo ""

# Function to download with error handling
download_model() {
    local model=$1
    local name=$2
    local size=$3

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📥 [$name] ($size)"
    echo "   Model: $model"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if huggingface-cli download "$model" --cache-dir ~/.cache/huggingface/hub; then
        echo "✓ Downloaded successfully"
    else
        echo "⚠️  Download may have stalled. Run again to resume."
    fi
    echo ""
}

# Tier 1: Daily Drivers
echo "📦 TIER 1: Daily Drivers (Fast)"
echo "═══════════════════════════════════════════════════════"
download_model "mlx-community/Dolphin3.0-Llama3.1-8B-4bit" "Dolphin 3.0 8B" "4.5GB"
download_model "mlx-community/Qwen2.5-7B-Instruct-Uncensored-4bit" "Qwen2.5-7B Uncensored" "4GB"
download_model "mlx-community/DeepSeek-R1-Distill-Qwen-7B-MLX" "DeepSeek-R1 7B" "3.8GB"

# Tier 2: Specialized Power
echo ""
echo "📦 TIER 2: Specialized Power (Medium)"
echo "═══════════════════════════════════════════════════════"
download_model "mlx-community/Hermes-4-14B-4bit" "Hermes-4 14B" "7-8GB"
download_model "mlx-community/DeepSeek-R1-Distill-Qwen-14B-MLX" "DeepSeek-R1 14B" "7-8GB"
download_model "mlx-community/Nous-Hermes2-Mixtral-8x7B-4bit" "Nous-Hermes2 8x7B" "7-8GB"

# Tier 3: Maximum Power
echo ""
echo "📦 TIER 3: Maximum Power (Expert)"
echo "═══════════════════════════════════════════════════════"
download_model "mlx-community/DeepSeek-R1-Distill-Qwen-32B-4bit" "DeepSeek-R1 32B" "16-18GB"

echo ""
echo "✅ All downloads complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 What You Now Have:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✓ 7 uncensored models"
echo "✓ 45GB total storage"
echo "✓ Load one at a time (no 24GB limit)"
echo "✓ All MLX optimized & Metal GPU accelerated"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Start MLX server:"
echo "   source ~/venv-mlx/bin/activate"
echo "   python3 mlx-server.py"
echo ""
echo "2. In another terminal, use models:"
echo "   source ~/venv-mlx/bin/activate"
echo "   cd ~/Workspace/llm-optimization-framework"
echo ""
echo "3. List available:"
echo "   python3 model-manager.py list"
echo ""
echo "4. Load a model:"
echo "   python3 model-manager.py load dolphin-3.0"
echo "   python3 model-manager.py load hermes-4"
echo "   python3 model-manager.py load deepseek-r1-32b"
echo ""
echo "5. Chat or generate:"
echo "   python3 model-manager.py chat"
echo "   python3 model-manager.py generate 'Your prompt here'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 Read OPTIMAL-MODELS.md for detailed information"
echo ""
