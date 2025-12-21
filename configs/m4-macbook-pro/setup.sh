#!/bin/bash
# Setup script for M4 MacBook Pro
# This script initializes the environment for MLX-based inference on Apple Silicon

set -e

MACHINE_ID="m4-macbook-pro"
VENV_PATH="configs/m4-macbook-pro/venv"
CONFIG_FILE="configs/m4-macbook-pro/ai-router-config.json"

echo "================================================"
echo "Setting up M4 MacBook Pro Environment"
echo "================================================"

# Create virtual environment
echo "[1/5] Creating Python virtual environment..."
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "[2/5] Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Upgrade pip
echo "[3/5] Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install MLX dependencies for Apple Silicon
echo "[4/5] Installing MLX and dependencies..."
pip install mlx mlx-lm numpy scipy pandas

# Create necessary directories
echo "[5/5] Creating model and cache directories..."
mkdir -p "configs/m4-macbook-pro/models"
mkdir -p "configs/m4-macbook-pro/cache"
mkdir -p "configs/m4-macbook-pro/logs"

# Write machine ID
echo "$MACHINE_ID" > .machine-id

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Activate environment: source $VENV_PATH/bin/activate"
echo "2. Download models: bash download-macbook-mlx.sh"
echo "3. Run router: python ai-router-mlx.py"
echo ""
echo "Configuration file: $CONFIG_FILE"
