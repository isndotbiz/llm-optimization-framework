#!/bin/bash
# Setup script for Xeon E5 + RTX 4060 Ti
# This script initializes the environment for quantized inference on limited VRAM

set -e

MACHINE_ID="xeon-4060ti"
VENV_PATH="configs/xeon-4060ti/venv"
CONFIG_FILE="configs/xeon-4060ti/ai-router-config.json"

echo "================================================"
echo "Setting up Xeon E5 + RTX 4060 Ti Environment"
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

# Install Ollama and quantized model support
echo "[5/6] Installing Ollama and quantization tools..."
pip install ollama llama-cpp-python torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate bitsandbytes

# Create necessary directories
echo "[6/6] Creating model and cache directories..."
mkdir -p "configs/xeon-4060ti/models"
mkdir -p "configs/xeon-4060ti/cache"
mkdir -p "configs/xeon-4060ti/logs"

# Write machine ID
echo "$MACHINE_ID" > .machine-id

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Machine Specs:"
echo "- CPU: Intel Xeon E5-2676v3 (12-core)"
echo "- GPU: NVIDIA RTX 4060 Ti (16GB VRAM)"
echo "- RAM: 16GB System Memory"
echo ""
echo "Important Notes:"
echo "- This machine uses quantized models (Q4) for efficiency"
echo "- Recommended max model size: 14B parameters"
echo "- Suitable for testing and constrained workloads"
echo ""
echo "Next steps:"
echo "1. Activate environment: source $VENV_PATH/bin/activate"
echo "2. Download models: bash download-gpu-models.sh (select Q4 models)"
echo "3. Run router: python ai-router.py"
echo ""
echo "Configuration file: $CONFIG_FILE"
