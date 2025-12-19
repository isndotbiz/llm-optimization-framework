# TrueNAS AI Router Deployment Guide
## RTX 4060 Ti Edition (16GB VRAM)

**Version**: 3.0 TrueNAS
**GPU**: NVIDIA RTX 4060 Ti (16GB VRAM)
**Framework**: llama.cpp with CUDA 12.x
**Server**: TrueNAS at 10.0.0.89
**Created**: 2025-12-14

---

## Table of Contents

1. [Overview](#overview)
2. [Hardware Requirements](#hardware-requirements)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Installation Steps](#installation-steps)
5. [Configuration](#configuration)
6. [Model Optimization Guide](#model-optimization-guide)
7. [API Usage](#api-usage)
8. [Troubleshooting](#troubleshooting)
9. [Performance Tuning](#performance-tuning)

---

## Overview

This guide covers deploying the AI Router on a TrueNAS server with RTX 4060 Ti GPU. The system provides:

- **Local CLI Interface**: Interactive menu system for managing models and projects
- **REST API**: Remote access via HTTP endpoints at `http://10.0.0.89:5000`
- **VRAM Monitoring**: Real-time GPU memory tracking
- **Model Management**: Project-based workflow for organizing prompts and conversations
- **4060 Ti Optimization**: Models carefully selected and quantized for 16GB VRAM

---

## Hardware Requirements

### GPU: RTX 4060 Ti
- **VRAM**: 16GB (crucial for this setup)
- **CUDA Capability**: 8.9 (Supported by CUDA 12.x)
- **Power**: 130W TDP
- **Driver**: NVIDIA Driver 550+ (CUDA 12.3+)

### CPU & Memory
- **CPU**: Any modern multicore processor (RTX 4060 Ti is main bottleneck)
- **System RAM**: 16GB+ recommended
- **NVMe Storage**: For model files (120-150GB total)

### Network
- **Ethernet**: 1Gbps minimum (for REST API clients)
- **Server IP**: 10.0.0.89 (update as needed)
- **Port**: 5000 (configurable)

---

## Pre-Deployment Checklist

- [ ] RTX 4060 Ti installed and detected by TrueNAS
- [ ] NVIDIA drivers installed (Driver version 550+)
- [ ] CUDA toolkit 12.3+ installed
- [ ] llama.cpp built with CUDA support
- [ ] Python 3.9+ installed
- [ ] Required Python packages available
- [ ] Storage location planned (/mnt/models recommended)
- [ ] TrueNAS dataset created for models
- [ ] Network IP address verified (10.0.0.89)

### Commands to Verify

```bash
# Check GPU detection
nvidia-smi

# Output should show:
# NVIDIA GeForce RTX 4060 Ti | Driver Version: 550.xx | CUDA Version: 12.x

# Check llama.cpp CUDA support
/root/llama.cpp/build/bin/llama-cli --help | grep -i gpu

# Check Python
python3 --version
```

---

## Installation Steps

### Step 1: Prepare Storage

```bash
# Create dataset on TrueNAS
# (Via Web UI: Storage > Pools > Create Dataset: models)

# Or via command line
zfs create tank/models

# Mount point structure
/mnt/models/
├── organized/          # GGUF model files
├── projects/           # Project configurations
├── system-prompts/     # System prompt files
└── logs/              # Application logs

# Create directories
mkdir -p /mnt/models/{organized,projects,logs}
chmod 755 /mnt/models
```

### Step 2: Install Python Dependencies

```bash
# SSH into TrueNAS
ssh root@10.0.0.89

# Update Python packages
pip3 install --upgrade pip setuptools wheel

# Install required packages
pip3 install flask psutil GPUtil

# Or use requirements file (create requirements.txt):
flask==3.0.0
psutil==6.0.0
GPUtil==1.4.0
```

### Step 3: Deploy AI Router

```bash
# Copy ai-router-truenas.py to TrueNAS
scp ai-router-truenas.py root@10.0.0.89:/mnt/models/

# Copy logging config
scp logging_config.py root@10.0.0.89:/mnt/models/

# SSH into TrueNAS and verify
ssh root@10.0.0.89
cd /mnt/models
ls -la
```

### Step 4: Verify llama.cpp Installation

```bash
# Check if already installed
ls -la /root/llama.cpp/build/bin/llama-cli

# If not installed, install from source:
cd /root
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build with CUDA support
mkdir build
cd build
cmake .. -DLLAMA_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89
cmake --build . --config Release

# Verify
./bin/llama-cli --version
```

### Step 5: Download and Organize Models

```bash
cd /mnt/models/organized

# Download GGUF files (use one of these methods)

# Option A: Using huggingface-hub
pip3 install huggingface-hub
huggingface-cli download cognitivecomputations/dolphin-3.0-llama3.1-8b-gguf Dolphin3.0-Llama3.1-8B-Q6_K.gguf

# Option B: Manual download
wget https://huggingface.co/cognitivecomputations/dolphin-3.0-llama3.1-8b-gguf/resolve/main/Dolphin3.0-Llama3.1-8B-Q6_K.gguf

# Option C: Using oobabooga web UI or similar

# Verify download
ls -lh *.gguf
```

### Step 6: Create System Prompts Directory

```bash
cd /mnt/models

# Create system-prompt files
cat > system-prompt-dolphin-8b.txt << 'EOF'
You are Dolphin, an uncensored and unbiased AI assistant. You provide helpful, harmless, and honest answers.
EOF

cat > system-prompt-phi4-14b.txt << 'EOF'
You are Phi-4, a reasoning expert. Approach problems systematically and think step-by-step.
EOF

# Add more system prompts as needed
```

### Step 7: First Run

```bash
cd /mnt/models

# Run the AI Router
python3 ai-router-truenas.py

# You should see the menu:
# ================================================================================
# TrueNAS AI ROUTER v3.0 - RTX 4060 Ti Edition
# ================================================================================

# Select option [1] to create a project
```

---

## Configuration

### Model Configuration Format

Each model in the database includes:

```python
"dolphin-llama31-8b": {
    "name": "Dolphin 3.0 Llama 3.1 8B Q6_K",
    "path": "/mnt/models/organized/Dolphin3.0-Llama3.1-8B-Q6_K.gguf",
    "size_gb": 6,                          # Critical for VRAM checking
    "speed": "60-85 tok/sec",
    "use_case": "Fast general tasks, uncensored chat",
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "context": 32768,
    "special_flags": [],                   # Model-specific flags
    "system_prompt": "system-prompt-dolphin-8b.txt",
    "framework": "llama.cpp",
    "optimal_for_4060ti": True             # RECOMMENDED models only
}
```

### Environment Variables (Optional)

```bash
# Create ~/.bashrc additions for TrueNAS user
export MODELS_DIR="/mnt/models"
export LLAMA_CPP_PATH="/root/llama.cpp/build/bin"
export CUDA_VISIBLE_DEVICES="0"  # Use GPU 0
export OMP_NUM_THREADS=12        # Match CPU cores

# Add to /root/.bashrc
echo 'export MODELS_DIR="/mnt/models"' >> /root/.bashrc
source /root/.bashrc
```

---

## Model Optimization Guide

### RTX 4060 Ti VRAM Management (16GB)

With 16GB VRAM, you can run:

#### ✅ OPTIMAL (Recommended)
- **Dolphin Llama 3.1 8B Q6_K**: 6GB - Best for speed
- **Phi-4 14B Q5_K_M**: 9GB - Best for reasoning
- **Qwen2.5 Coder 14B Q5_K_M**: 9GB - Best for coding
- **Gemma-3 9B Q6_K**: 7GB - Best for long context
- **Ministral-3 14B Q5_K_M**: 9GB - Excellent all-around

#### ⚠️ TIGHT FIT (Use with caution)
- **Dolphin Mistral 24B Q4_K_M**: 14GB - Leaves 2GB free
- **Qwen3 Coder 30B Q4_K_M**: 18GB - REQUIRES careful quantization

#### 🚫 NOT RECOMMENDED
- **Llama 3.3 70B**: Even IQ2_S (15GB) leaves no headroom

### Model Size Formula

```
Model Size (GB) ≈ (Parameters in B) × (Quantization Bits / 8) × 1.1

Examples:
- 8B model × 6-bit (Q6_K) ≈ 6GB
- 14B model × 5-bit (Q5_K_M) ≈ 9GB
- 24B model × 4-bit (Q4_K_M) ≈ 14GB
```

### Quantization Levels Explained

| Quant | Bits | Size Impact | Quality | Speed |
|-------|------|-------------|---------|-------|
| Q2_K | 2.5 | 3-4GB (70B) | Poor | Fastest |
| Q3_K | 3.5 | 5-6GB (14B) | Fair | Very Fast |
| Q4_K_M | 4.3 | 7GB (14B) | Good | Fast |
| Q5_K_M | 5.3 | 9GB (14B) | Very Good | Medium |
| Q6_K | 6.6 | 11GB (14B) | Excellent | Medium-Slow |
| Q8_0 | 8.0 | 13GB (14B) | Near-Lossless | Slow |

### Selecting Models for Your Use Case

**Programming/Coding**:
- Primary: Qwen2.5 Coder 14B Q5_K_M (9GB)
- Fast: Phi-4 14B Q5_K_M (9GB)

**General Chat/Writing**:
- Primary: Dolphin Llama 3.1 8B Q6_K (6GB)
- Creative: Dolphin Mistral 24B Q4_K_M (14GB)

**Reasoning/Math**:
- Primary: Phi-4 14B Q5_K_M (9GB)
- Extended: Ministral-3 14B Q5_K_M (9GB, 256K context)

**Long Context (documents, code analysis)**:
- Primary: Gemma-3 9B Q6_K (7GB, 128K context)
- Reasoning: Ministral-3 14B Q5_K_M (9GB, 256K context)

---

## API Usage

### Starting the API Server

```bash
cd /mnt/models

# Run with API enabled
python3 ai-router-truenas.py

# Select [7] "Start REST API Server"
# Server starts on http://10.0.0.89:5000
```

### API Endpoints

#### Health Check
```bash
curl http://10.0.0.89:5000/api/health

# Response:
{
  "status": "healthy",
  "gpu_vram": {
    "used_gb": 6.5,
    "total_gb": 16,
    "free_gb": 9.5,
    "percent": 40.6
  }
}
```

#### List Available Models
```bash
curl http://10.0.0.89:5000/api/models

# Response:
{
  "total": 8,
  "optimal": 5,
  "models": {
    "dolphin-llama31-8b": {"name": "Dolphin 3.0 Llama 3.1 8B Q6_K", "size_gb": 6},
    ...
  }
}
```

#### List Projects
```bash
curl http://10.0.0.89:5000/api/projects

# Response:
{
  "projects": ["coding-project", "chatbot", "research"]
}
```

#### Run Inference
```bash
curl -X POST http://10.0.0.89:5000/api/infer \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "dolphin-llama31-8b",
    "prompt": "Explain quantum computing"
  }'

# Response:
{
  "status": "success",
  "message": "Model executed"
}
```

### Python Client Example

```python
import requests
import json

API_URL = "http://10.0.0.89:5000"

# Check health
health = requests.get(f"{API_URL}/api/health").json()
print(f"GPU Usage: {health['gpu_vram']['percent']}%")

# List models
models = requests.get(f"{API_URL}/api/models").json()
for model_id, info in models['models'].items():
    print(f"{model_id}: {info['name']} ({info['size_gb']}GB)")

# Run inference
response = requests.post(
    f"{API_URL}/api/infer",
    json={
        "model_id": "dolphin-llama31-8b",
        "prompt": "What is the capital of France?"
    }
)
print(response.json())
```

---

## Troubleshooting

### GPU Not Detected

```bash
# Check driver
nvidia-smi

# If not found, install/update drivers
# On TrueNAS, may need to compile kernel module:
# (Consult TrueNAS documentation for your version)

# Verify CUDA is discoverable
ldconfig -p | grep libcuda
```

### VRAM Errors

```bash
# Check current usage
nvidia-smi

# If OOM (Out of Memory):
# 1. Close other GPU applications
# 2. Use smaller quantization (Q4 instead of Q6)
# 3. Reduce context window
# 4. Use smaller model

# Monitor in real-time
watch -n 1 nvidia-smi
```

### Model Not Loading

```bash
# Verify model file exists and is readable
ls -lh /mnt/models/organized/*.gguf

# Test llama.cpp directly
/root/llama.cpp/build/bin/llama-cli \
  -m /mnt/models/organized/Dolphin3.0-Llama3.1-8B-Q6_K.gguf \
  -p "test" \
  -n 1 \
  --verbose-prompt

# If errors, check:
# - Model format (must be GGUF)
# - File corruption (redownload)
# - Permissions (chmod 644)
```

### API Not Responding

```bash
# Check Flask is installed
python3 -c "import flask; print(flask.__version__)"

# If missing:
pip3 install flask

# Check port availability
netstat -tlnp | grep 5000

# Try different port in code (edit ai-router-truenas.py):
# self.api_port = 5001  # Use 5001 instead
```

### Slow Performance

```bash
# 1. Check if model is on GPU
/root/llama.cpp/build/bin/llama-cli -m model.gguf -p "test" -ngl 999 -t 12

# Output should show "ggml_cuda_init" - means GPU is being used

# 2. Reduce batch size if needed
# 3. Check for thermal throttling
# 4. Verify no other heavy GPU processes

# Benchmarking command
time /root/llama.cpp/build/bin/llama-cli \
  -m /mnt/models/organized/Dolphin3.0-Llama3.1-8B-Q6_K.gguf \
  -p "Explain the theory of relativity in 100 words." \
  -n 100 \
  -ngl 999 \
  -t 12
```

---

## Performance Tuning

### Optimal Inference Parameters

For RTX 4060 Ti with different model sizes:

#### 8B Models (Dolphin)
```
-ngl 999              # Offload all layers to GPU
-t 12                 # Use 12 CPU threads (adjust for your CPU)
-b 512                # Batch size
-ub 512               # Ubatch size (for parallel requests)
--cache-type-k q8_0   # Quantize cache for VRAM savings
--cache-type-v q8_0
```

#### 14B Models (Phi, Qwen, Ministral)
```
-ngl 999              # All to GPU
-t 8                  # Slightly fewer threads
-b 256                # Smaller batches
-ub 256
--cache-type-k q8_0
--cache-type-v q8_0
```

#### 24B Models (Dolphin Mistral)
```
-ngl 999              # All to GPU
-t 6                  # Fewer threads
-b 128                # Small batches
-ub 128
--cache-type-k q4_0   # More aggressive quantization
--cache-type-v q4_0
```

### CUDA Optimization Flags

```bash
# For maximum speed on RTX 4060 Ti:
export CUDA_LAUNCH_BLOCKING=0        # Async CUDA calls
export CUDA_DEVICE_ORDER=PCI_BUS_ID  # Consistent GPU ordering
export CUDA_VISIBLE_DEVICES=0        # Use GPU 0

# In llama.cpp command:
-fa 1                 # Flash attention (faster, less VRAM)
-ptc 10               # Print token count
```

### Temperature Management

```bash
# Monitor GPU temperature
watch -n 1 "nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader"

# Typical RTX 4060 Ti limits:
# - Throttle temp: 83°C
# - Shutdown temp: 93°C
# - Ideal operating: 60-75°C

# If running hot:
# 1. Reduce batch size (-b 256)
# 2. Use lower quantization (Q4 instead of Q6)
# 3. Increase ventilation
# 4. Check thermal paste quality
```

### Memory Efficiency

```bash
# Check model actual VRAM usage
nvidia-smi --query-compute-apps=pid,process_name,memory.used --format=csv

# If model uses less than expected, you can run multiple instances
# Set CUDA_VISIBLE_DEVICES per process:
CUDA_VISIBLE_DEVICES=0 python3 process1.py &
CUDA_VISIBLE_DEVICES=0 python3 process2.py &
```

---

## Next Steps

1. **Customize System Prompts**: Edit system-prompt files for your use case
2. **Add More Models**: Update ModelDatabase in ai-router-truenas.py
3. **Setup Monitoring**: Configure TrueNAS alerts for GPU temperature
4. **Enable HTTPS**: Wrap API with nginx reverse proxy + SSL
5. **Backup Strategy**: Regular backups of projects and conversations

---

## Support & Feedback

For issues or suggestions:
- Check logs: `/mnt/models/logs/ai-router-*.log`
- Review troubleshooting section above
- Consult TrueNAS documentation for hardware setup
- Check llama.cpp GitHub for CUDA-specific issues

---

## License & Attribution

Built on the Open Source AI Router framework with optimizations for RTX 4060 Ti.
Uses llama.cpp for model execution.

**Deployment Date**: 2025-12-14
**System IP**: 10.0.0.89
**API Port**: 5000
