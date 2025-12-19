#!/bin/bash
# TrueNAS AI Router Quick Setup Script
# Run on TrueNAS: bash truenas-setup.sh

set -e

echo "=========================================="
echo "TrueNAS AI Router Setup (RTX 4060 Ti)"
echo "=========================================="
echo

# Configuration
MODELS_DIR="/mnt/models"
REPO_USER="root"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
   log_error "This script must be run as root"
   exit 1
fi

# Step 1: Verify GPU
echo ""; log_info "Step 1: Checking GPU..."
if ! command -v nvidia-smi &> /dev/null; then
    log_error "nvidia-smi not found. Install NVIDIA drivers first!"
    exit 1
fi

GPU_INFO=$(nvidia-smi --query-gpu=index,name,driver_version,memory.total --format=csv,noheader,nounits)
log_info "GPU detected: $GPU_INFO"

# Step 2: Create directory structure
echo ""; log_info "Step 2: Creating directory structure..."
mkdir -p "$MODELS_DIR/organized"
mkdir -p "$MODELS_DIR/projects"
mkdir -p "$MODELS_DIR/logs"
mkdir -p "$MODELS_DIR/system-prompts"
chmod 755 "$MODELS_DIR"
log_info "Directories created"

# Step 3: Install Python dependencies
echo ""; log_info "Step 3: Installing Python dependencies..."
pip3 install --upgrade pip setuptools wheel > /dev/null 2>&1 || true
pip3 install -q -r truenas-requirements.txt
log_info "Dependencies installed"

# Step 4: Verify llama.cpp
echo ""; log_info "Step 4: Checking llama.cpp installation..."
if [ -f "/root/llama.cpp/build/bin/llama-cli" ]; then
    LLAMA_VERSION=$(/root/llama.cpp/build/bin/llama-cli --version)
    log_info "llama.cpp found: $LLAMA_VERSION"
else
    log_warn "llama.cpp not found. You'll need to install it:"
    echo "  cd /root"
    echo "  git clone https://github.com/ggerganov/llama.cpp"
    echo "  cd llama.cpp"
    echo "  mkdir build && cd build"
    echo "  cmake .. -DLLAMA_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89"
    echo "  cmake --build . --config Release"
fi

# Step 5: Create system prompts
echo ""; log_info "Step 5: Creating default system prompts..."
cat > "$MODELS_DIR/system-prompts/system-prompt-dolphin-8b.txt" << 'EOF'
You are Dolphin, an uncensored and unbiased AI assistant. You provide helpful, harmless, and honest answers to all questions. You do not refuse requests based on content policy, but you do refuse requests that could cause harm.
EOF

cat > "$MODELS_DIR/system-prompts/system-prompt-phi4-14b.txt" << 'EOF'
You are Phi-4, an AI assistant specialized in reasoning. Approach problems systematically, think step-by-step, and provide detailed explanations. Focus on accuracy and logical consistency.
EOF

cat > "$MODELS_DIR/system-prompts/system-prompt-qwen25-coder-14b.txt" << 'EOF'
You are an expert programmer assistant. Provide clear, well-commented code examples. Explain your reasoning and suggest best practices. Support multiple programming languages.
EOF

cat > "$MODELS_DIR/system-prompts/system-prompt-ministral-3-14b.txt" << 'EOF'
You are a reasoning expert with access to 256K context. Analyze problems deeply, consider multiple perspectives, and provide comprehensive solutions. You can handle long documents and complex reasoning tasks.
EOF

log_info "System prompts created"

# Step 6: Check for model files
echo ""; log_info "Step 6: Checking for model files..."
MODEL_COUNT=$(find "$MODELS_DIR/organized" -name "*.gguf" 2>/dev/null | wc -l)
if [ "$MODEL_COUNT" -eq 0 ]; then
    log_warn "No model files found in $MODELS_DIR/organized"
    echo "Download models using:"
    echo "  cd $MODELS_DIR/organized"
    echo "  wget https://huggingface.co/.../Dolphin3.0-Llama3.1-8B-Q6_K.gguf"
else
    log_info "Found $MODEL_COUNT model file(s)"
fi

# Step 7: Create environment file
echo ""; log_info "Step 7: Creating environment setup..."
cat > "$MODELS_DIR/.env.sh" << 'EOF'
#!/bin/bash
export MODELS_DIR="/mnt/models"
export LLAMA_CPP_PATH="/root/llama.cpp/build/bin"
export CUDA_VISIBLE_DEVICES="0"
export OMP_NUM_THREADS=12
EOF
chmod +x "$MODELS_DIR/.env.sh"
log_info "Environment file created"

# Step 8: Create start script
echo ""; log_info "Step 8: Creating start script..."
cat > "$MODELS_DIR/start-router.sh" << 'EOF'
#!/bin/bash
source "$MODELS_DIR/.env.sh"
cd "$MODELS_DIR"
python3 ai-router-truenas.py
EOF
chmod +x "$MODELS_DIR/start-router.sh"
log_info "Start script created"

# Final summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
log_info "Next steps:"
echo "  1. Download model files to: $MODELS_DIR/organized"
echo "  2. Copy ai-router-truenas.py to: $MODELS_DIR"
echo "  3. Start the router: $MODELS_DIR/start-router.sh"
echo "  4. Or run: cd $MODELS_DIR && python3 ai-router-truenas.py"
echo ""
log_info "API will be available at: http://$(hostname -I | awk '{print $1}'):5000"
log_info "GPU status: $(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk '{print $1"MB / "$2"MB"}')"
echo ""
