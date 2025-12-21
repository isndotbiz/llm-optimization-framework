#!/bin/bash
# Setup script for Ryzen 9 + RTX 3090
# This script initializes the environment for CUDA-accelerated inference on Linux

set -e

MACHINE_ID="ryzen-9-3090"
VENV_PATH="configs/ryzen-9-3090/venv"
CONFIG_FILE="configs/ryzen-9-3090/ai-router-config.json"

echo "================================================"
echo "Setting up Ryzen 9 + RTX 3090 Environment"
echo "================================================"

# Check for CUDA
echo "[1/6] Checking for CUDA..."
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "⚠ WARNING: nvidia-smi not found. CUDA may not be properly installed."
    echo "  Install CUDA Toolkit 12.1+ from: https://developer.nvidia.com/cuda-downloads"
fi

# Create virtual environment
echo "[2/6] Creating Python virtual environment..."
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "[3/6] Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Upgrade pip
echo "[4/6] Upgrading pip and installing build tools..."
pip install --upgrade pip setuptools wheel

# Install CUDA-compatible dependencies
echo "[5/6] Installing vLLM and CUDA dependencies..."
pip install vllm torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate bitsandbytes

# Create necessary directories
echo "[6/6] Creating model and cache directories..."
mkdir -p "configs/ryzen-9-3090/models"
mkdir -p "configs/ryzen-9-3090/cache"
mkdir -p "configs/ryzen-9-3090/logs"

# Write machine ID
echo "$MACHINE_ID" > .machine-id

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Machine Specs:"
echo "- CPU: AMD Ryzen 9 (16-core)"
echo "- GPU: NVIDIA RTX 3090 (24GB VRAM)"
echo "- RAM: 24GB System Memory"
echo ""
echo "Next steps:"
echo "1. Activate environment: source $VENV_PATH/bin/activate"
echo "2. Download models: bash download-gpu-models.sh"
echo "3. Run router: python ai-router.py"
echo ""
echo "Configuration file: $CONFIG_FILE"
