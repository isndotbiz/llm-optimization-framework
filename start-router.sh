#!/bin/bash

echo "Freeing up GPU memory..."
echo ""

# Kill any existing llama.cpp processes
pkill -f llama-cli
pkill -f llama.cpp
pkill -f "ai-router"

# Wait a moment for processes to terminate
sleep 1

# Check GPU status if nvidia-smi is available
if command -v nvidia-smi &> /dev/null; then
    echo "GPU Status before cleanup:"
    nvidia-smi
    echo ""
    echo "Clearing GPU cache..."
    nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | xargs -I {} echo "GPU Memory in use: {} MB"
else
    echo "nvidia-smi not available - GPU monitoring disabled"
fi

echo ""
echo "Starting AI Router Enhanced..."
echo ""

cd /mnt/d/models
python3 ai-router-enhanced.py
