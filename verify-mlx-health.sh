#!/bin/bash
###############################################################################
# MLX Health Check Script
# Comprehensive validation of MLX installation and performance
# Version: 1.0
# Date: 2025-12-19
###############################################################################

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

# Unicode symbols
CHECK="✓"
CROSS="✗"
INFO="ℹ"
WARN="⚠"
ROCKET="🚀"

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNING_TESTS=0

# System info
SYSTEM_READY=true
ERRORS=()
WARNINGS=()

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "\n${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${CYAN}${BOLD}  $1${RESET}"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
}

print_section() {
    echo -e "\n${BLUE}${BOLD}▶ $1${RESET}"
}

print_test() {
    echo -e "${DIM}  Testing: $1${RESET}"
}

print_pass() {
    ((TOTAL_TESTS++))
    ((PASSED_TESTS++))
    echo -e "  ${GREEN}${CHECK} PASS${RESET} - $1"
}

print_fail() {
    ((TOTAL_TESTS++))
    ((FAILED_TESTS++))
    SYSTEM_READY=false
    ERRORS+=("$1")
    echo -e "  ${RED}${CROSS} FAIL${RESET} - $1"
    if [ -n "$2" ]; then
        echo -e "    ${DIM}→ $2${RESET}"
    fi
}

print_warn() {
    ((TOTAL_TESTS++))
    ((WARNING_TESTS++))
    WARNINGS+=("$1")
    echo -e "  ${YELLOW}${WARN} WARN${RESET} - $1"
    if [ -n "$2" ]; then
        echo -e "    ${DIM}→ $2${RESET}"
    fi
}

print_info() {
    echo -e "  ${CYAN}${INFO}${RESET} $1"
}

print_value() {
    echo -e "    ${WHITE}$1:${RESET} ${GREEN}$2${RESET}"
}

###############################################################################
# Banner
###############################################################################

print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "                    MLX HEALTH CHECK v1.0"
    echo "            Comprehensive MLX Installation Validation"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${RESET}"
    echo -e "${DIM}Date: $(date '+%Y-%m-%d %H:%M:%S')${RESET}\n"
}

###############################################################################
# Test 1: System Requirements
###############################################################################

test_system_requirements() {
    print_header "1. SYSTEM REQUIREMENTS"

    # Check OS
    print_section "Operating System"
    OS_TYPE=$(uname -s)
    if [ "$OS_TYPE" = "Darwin" ]; then
        OS_VERSION=$(sw_vers -productVersion)
        print_pass "macOS detected: $OS_VERSION"

        # Check macOS version (need 12.0+)
        MAJOR_VERSION=$(echo "$OS_VERSION" | cut -d. -f1)
        if [ "$MAJOR_VERSION" -ge 12 ]; then
            print_pass "macOS version is compatible (≥12.0)"
        else
            print_fail "macOS version too old: $OS_VERSION" "Requires macOS 12.0 or later"
        fi
    else
        print_fail "Not running on macOS: $OS_TYPE" "MLX requires macOS"
        return 1
    fi

    # Check architecture
    print_section "CPU Architecture"
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ]; then
        print_pass "Apple Silicon detected: $ARCH"

        # Try to get specific chip info
        CHIP_INFO=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Apple Silicon")
        print_info "Chip: $CHIP_INFO"
    else
        print_fail "Not Apple Silicon: $ARCH" "MLX requires M1/M2/M3/M4 chip"
        return 1
    fi

    # Check RAM
    print_section "Memory (RAM)"
    RAM_BYTES=$(sysctl -n hw.memsize)
    RAM_GB=$((RAM_BYTES / 1024 / 1024 / 1024))
    print_value "Total RAM" "${RAM_GB}GB"

    if [ "$RAM_GB" -ge 32 ]; then
        print_pass "RAM is excellent: ${RAM_GB}GB (can run all models)"
    elif [ "$RAM_GB" -ge 16 ]; then
        print_pass "RAM is good: ${RAM_GB}GB (can run 7B-14B models)"
        print_warn "32B models may require closing other apps" "Consider 32GB+ for large models"
    else
        print_warn "RAM is low: ${RAM_GB}GB" "Minimum 16GB recommended for MLX"
    fi

    # Check available disk space
    print_section "Disk Space"
    AVAILABLE_GB=$(df -g ~ | awk 'NR==2 {print $4}')
    print_value "Available space" "${AVAILABLE_GB}GB"

    if [ "$AVAILABLE_GB" -ge 100 ]; then
        print_pass "Disk space is excellent: ${AVAILABLE_GB}GB"
    elif [ "$AVAILABLE_GB" -ge 50 ]; then
        print_pass "Disk space is adequate: ${AVAILABLE_GB}GB"
    else
        print_warn "Disk space is low: ${AVAILABLE_GB}GB" "Recommended 50GB+ for multiple models"
    fi
}

###############################################################################
# Test 2: Python Environment
###############################################################################

test_python_environment() {
    print_header "2. PYTHON ENVIRONMENT"

    # Check Python version
    print_section "Python Installation"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        print_pass "Python3 found: $PYTHON_VERSION"

        # Check if version is 3.8+
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_pass "Python version is compatible (≥3.8)"
        else
            print_fail "Python version too old: $PYTHON_VERSION" "Requires Python 3.8+"
        fi
    else
        print_fail "Python3 not found" "Install with: brew install python3"
        return 1
    fi

    # Check for virtual environment
    print_section "Virtual Environment"
    VENV_PATH="$HOME/workspace/venv-mlx"
    if [ -d "$VENV_PATH" ]; then
        print_pass "MLX venv found: $VENV_PATH"

        # Check if venv has Python
        if [ -f "$VENV_PATH/bin/python3" ]; then
            print_pass "Virtual environment is valid"
        else
            print_fail "Virtual environment is corrupted" "Recreate with: python3 -m venv $VENV_PATH"
        fi
    else
        print_warn "MLX venv not found at: $VENV_PATH" "Create with: python3 -m venv $VENV_PATH"
    fi

    # Check pip
    print_section "Package Manager (pip)"
    if [ -f "$VENV_PATH/bin/pip" ]; then
        PIP_VERSION=$("$VENV_PATH/bin/pip" --version | awk '{print $2}')
        print_pass "pip found in venv: $PIP_VERSION"
    else
        print_warn "pip not found in venv" "Activate venv and run: pip install --upgrade pip"
    fi
}

###############################################################################
# Test 3: MLX Installation
###############################################################################

test_mlx_installation() {
    print_header "3. MLX INSTALLATION"

    VENV_PATH="$HOME/workspace/venv-mlx"

    if [ ! -f "$VENV_PATH/bin/python3" ]; then
        print_fail "Virtual environment not found" "Cannot test MLX installation"
        return 1
    fi

    # Activate venv and test
    print_section "MLX Core Library"

    # Test MLX import and version
    MLX_TEST_OUTPUT=$("$VENV_PATH/bin/python3" -c "
import sys
try:
    import mlx.core as mx
    print(f'VERSION:{mx.__version__}')
    print(f'METAL:{mx.metal.is_available()}')
    print(f'DEVICE:{mx.default_device()}')
except ImportError as e:
    print(f'ERROR:{e}')
    sys.exit(1)
" 2>&1)

    if echo "$MLX_TEST_OUTPUT" | grep -q "ERROR:"; then
        ERROR_MSG=$(echo "$MLX_TEST_OUTPUT" | grep "ERROR:" | cut -d: -f2-)
        print_fail "MLX not installed: $ERROR_MSG" "Install with: pip install mlx"
        return 1
    else
        MLX_VERSION=$(echo "$MLX_TEST_OUTPUT" | grep "VERSION:" | cut -d: -f2)
        METAL_AVAILABLE=$(echo "$MLX_TEST_OUTPUT" | grep "METAL:" | cut -d: -f2)
        DEFAULT_DEVICE=$(echo "$MLX_TEST_OUTPUT" | grep "DEVICE:" | cut -d: -f2)

        print_pass "MLX Core installed: v$MLX_VERSION"
        print_value "Metal available" "$METAL_AVAILABLE"
        print_value "Default device" "$DEFAULT_DEVICE"

        if [ "$METAL_AVAILABLE" = "True" ]; then
            print_pass "Metal GPU support is active"
        else
            print_fail "Metal GPU support not available" "MLX requires Metal support"
        fi
    fi

    # Test MLX LM
    print_section "MLX LM (Language Models)"
    MLX_LM_TEST=$("$VENV_PATH/bin/python3" -c "
try:
    import mlx_lm
    print('INSTALLED')
except ImportError:
    print('NOT_INSTALLED')
" 2>&1)

    if [ "$MLX_LM_TEST" = "INSTALLED" ]; then
        print_pass "MLX LM installed"

        # Check if mlx_lm.chat command exists
        if [ -f "$VENV_PATH/bin/mlx_lm.chat" ] || "$VENV_PATH/bin/python3" -m mlx_lm.chat --help &>/dev/null; then
            print_pass "mlx_lm.chat command available"
        else
            print_warn "mlx_lm.chat command not found" "May need to reinstall: pip install -U mlx-lm"
        fi
    else
        print_fail "MLX LM not installed" "Install with: pip install mlx-lm"
    fi

    # Check for other dependencies
    print_section "Dependencies"
    for pkg in numpy transformers; do
        if "$VENV_PATH/bin/python3" -c "import $pkg" 2>/dev/null; then
            print_pass "$pkg installed"
        else
            print_warn "$pkg not installed" "Install with: pip install $pkg"
        fi
    done
}

###############################################################################
# Test 4: Metal GPU Support
###############################################################################

test_metal_gpu() {
    print_header "4. METAL GPU SUPPORT"

    VENV_PATH="$HOME/workspace/venv-mlx"

    if [ ! -f "$VENV_PATH/bin/python3" ]; then
        print_fail "Cannot test Metal GPU" "Virtual environment not found"
        return 1
    fi

    print_section "GPU Detection"

    # Get detailed Metal info
    GPU_INFO=$("$VENV_PATH/bin/python3" << 'EOF'
import mlx.core as mx

try:
    # Check Metal availability
    metal_available = mx.metal.is_available()
    default_device = str(mx.default_device())

    # Try to get memory info
    try:
        active_mem = mx.metal.get_active_memory() / 1e9
        cache_mem = mx.metal.get_cache_memory() / 1e9
        peak_mem = mx.metal.get_peak_memory() / 1e9
        print(f"METAL_AVAILABLE:{metal_available}")
        print(f"DEFAULT_DEVICE:{default_device}")
        print(f"ACTIVE_MEMORY:{active_mem:.2f}")
        print(f"CACHE_MEMORY:{cache_mem:.2f}")
        print(f"PEAK_MEMORY:{peak_mem:.2f}")
    except Exception as e:
        print(f"METAL_AVAILABLE:{metal_available}")
        print(f"DEFAULT_DEVICE:{default_device}")
        print(f"MEMORY_ERROR:{e}")
except Exception as e:
    print(f"ERROR:{e}")
EOF
)

    if echo "$GPU_INFO" | grep -q "ERROR:"; then
        ERROR_MSG=$(echo "$GPU_INFO" | grep "ERROR:" | cut -d: -f2-)
        print_fail "Failed to query Metal GPU: $ERROR_MSG"
    else
        METAL=$(echo "$GPU_INFO" | grep "METAL_AVAILABLE:" | cut -d: -f2)
        DEVICE=$(echo "$GPU_INFO" | grep "DEFAULT_DEVICE:" | cut -d: -f2)

        if [ "$METAL" = "True" ]; then
            print_pass "Metal GPU detected and active"
            print_value "Device" "$DEVICE"

            # Memory info
            if echo "$GPU_INFO" | grep -q "ACTIVE_MEMORY:"; then
                ACTIVE=$(echo "$GPU_INFO" | grep "ACTIVE_MEMORY:" | cut -d: -f2)
                CACHE=$(echo "$GPU_INFO" | grep "CACHE_MEMORY:" | cut -d: -f2)
                PEAK=$(echo "$GPU_INFO" | grep "PEAK_MEMORY:" | cut -d: -f2)

                print_value "Active GPU memory" "${ACTIVE}GB"
                print_value "Cached GPU memory" "${CACHE}GB"
                print_value "Peak GPU memory" "${PEAK}GB"
                print_pass "GPU memory tracking is working"
            fi
        else
            print_fail "Metal GPU not available"
        fi
    fi

    # Test simple GPU computation
    print_section "GPU Computation Test"
    COMPUTE_TEST=$("$VENV_PATH/bin/python3" << 'EOF'
import mlx.core as mx
import time

try:
    # Create random arrays
    x = mx.random.normal(shape=(1000, 1000))
    y = mx.random.normal(shape=(1000, 1000))

    # Matrix multiplication on GPU
    start = time.time()
    z = mx.matmul(x, y)
    mx.eval(z)  # Force evaluation
    elapsed = time.time() - start

    print(f"SUCCESS:{elapsed*1000:.2f}")
except Exception as e:
    print(f"ERROR:{e}")
EOF
)

    if echo "$COMPUTE_TEST" | grep -q "ERROR:"; then
        ERROR_MSG=$(echo "$COMPUTE_TEST" | grep "ERROR:" | cut -d: -f2-)
        print_fail "GPU computation failed: $ERROR_MSG"
    else
        ELAPSED=$(echo "$COMPUTE_TEST" | grep "SUCCESS:" | cut -d: -f2)
        print_pass "GPU computation successful (${ELAPSED}ms)"

        # Warn if too slow
        if (( $(echo "$ELAPSED > 100" | bc -l) )); then
            print_warn "GPU computation is slow (${ELAPSED}ms)" "Expected <50ms for simple operations"
        fi
    fi
}

###############################################################################
# Test 5: Available Models
###############################################################################

test_available_models() {
    print_header "5. AVAILABLE MODELS"

    print_section "Model Cache Directory"

    CACHE_DIR="$HOME/.cache/huggingface/hub"
    if [ -d "$CACHE_DIR" ]; then
        print_pass "Hugging Face cache found: $CACHE_DIR"

        CACHE_SIZE=$(du -sh "$CACHE_DIR" 2>/dev/null | awk '{print $1}')
        print_value "Cache size" "$CACHE_SIZE"
    else
        print_warn "Hugging Face cache not found" "Models will download on first use"
    fi

    print_section "MLX Community Models"

    # List MLX models
    if [ -d "$CACHE_DIR" ]; then
        MLX_MODELS=$(ls -d "$CACHE_DIR"/models--mlx-community--* 2>/dev/null | wc -l | tr -d ' ')

        if [ "$MLX_MODELS" -gt 0 ]; then
            print_pass "Found $MLX_MODELS MLX model(s)"

            echo -e "\n${DIM}  Installed models:${RESET}"
            for model_dir in "$CACHE_DIR"/models--mlx-community--*; do
                if [ -d "$model_dir" ]; then
                    model_name=$(basename "$model_dir" | sed 's/models--mlx-community--//')
                    model_size=$(du -sh "$model_dir" 2>/dev/null | awk '{print $1}')
                    echo -e "    ${GREEN}•${RESET} ${WHITE}$model_name${RESET} ${DIM}($model_size)${RESET}"
                fi
            done
        else
            print_warn "No MLX models found" "Download with: mlx_lm.generate --model mlx-community/MODEL_NAME --max-tokens 1"
        fi
    fi

    # Check for recommended models
    print_section "Recommended Models Status"

    RECOMMENDED_MODELS=(
        "Qwen2.5-Coder-7B-Instruct-4bit:Fast coding (60-80 tok/sec)"
        "Qwen2.5-Coder-32B-Instruct-4bit:Best quality coding (15-22 tok/sec)"
        "DeepSeek-R1-Distill-Llama-8B:Reasoning & math (50-70 tok/sec)"
        "phi-4-4bit:STEM & technical (40-60 tok/sec)"
        "Mistral-7B-Instruct-v0.3-4bit:Ultra-fast general (70-100 tok/sec)"
    )

    for model_info in "${RECOMMENDED_MODELS[@]}"; do
        model_name=$(echo "$model_info" | cut -d: -f1)
        model_desc=$(echo "$model_info" | cut -d: -f2)

        if [ -d "$CACHE_DIR/models--mlx-community--$model_name" ]; then
            print_pass "$model_name"
        else
            echo -e "  ${DIM}○${RESET} $model_name ${DIM}(not installed)${RESET}"
            echo -e "    ${DIM}→ $model_desc${RESET}"
        fi
    done
}

###############################################################################
# Test 6: Model Loading & Inference
###############################################################################

test_model_loading() {
    print_header "6. MODEL LOADING & INFERENCE"

    VENV_PATH="$HOME/workspace/venv-mlx"

    if [ ! -f "$VENV_PATH/bin/python3" ]; then
        print_fail "Cannot test model loading" "Virtual environment not found"
        return 1
    fi

    # Find a model to test with
    CACHE_DIR="$HOME/.cache/huggingface/hub"
    TEST_MODEL=""

    # Try to find Qwen2.5-Coder-7B first (fastest)
    if [ -d "$CACHE_DIR/models--mlx-community--Qwen2.5-Coder-7B-Instruct-4bit" ]; then
        TEST_MODEL="mlx-community/Qwen2.5-Coder-7B-Instruct-4bit"
    else
        # Find any MLX model
        FIRST_MODEL=$(ls -d "$CACHE_DIR"/models--mlx-community--* 2>/dev/null | head -1)
        if [ -n "$FIRST_MODEL" ]; then
            TEST_MODEL="mlx-community/$(basename "$FIRST_MODEL" | sed 's/models--mlx-community--//')"
        fi
    fi

    if [ -z "$TEST_MODEL" ]; then
        print_warn "No models available for testing" "Download a model first"
        return 0
    fi

    print_section "Model Loading Test"
    print_info "Testing with: $TEST_MODEL"

    # Test model loading
    LOAD_TEST=$("$VENV_PATH/bin/python3" << EOF
import time
from mlx_lm import load
import mlx.core as mx

model_name = "$TEST_MODEL"

try:
    print("Loading model...", flush=True)
    start = time.time()
    model, tokenizer = load(model_name)
    load_time = time.time() - start

    # Get memory usage
    mem_gb = mx.metal.get_active_memory() / 1e9

    print(f"LOAD_TIME:{load_time:.3f}")
    print(f"MEMORY:{mem_gb:.2f}")
    print("SUCCESS")
except Exception as e:
    print(f"ERROR:{e}")
EOF
)

    if echo "$LOAD_TEST" | grep -q "ERROR:"; then
        ERROR_MSG=$(echo "$LOAD_TEST" | grep "ERROR:" | cut -d: -f2-)
        print_fail "Model loading failed: $ERROR_MSG"
    elif echo "$LOAD_TEST" | grep -q "SUCCESS"; then
        LOAD_TIME=$(echo "$LOAD_TEST" | grep "LOAD_TIME:" | cut -d: -f2)
        MEMORY=$(echo "$LOAD_TEST" | grep "MEMORY:" | cut -d: -f2)

        print_pass "Model loaded successfully in ${LOAD_TIME}s"
        print_value "Memory used" "${MEMORY}GB"

        # Performance check
        if (( $(echo "$LOAD_TIME < 2.0" | bc -l) )); then
            print_pass "Load time is excellent (<2s)"
        elif (( $(echo "$LOAD_TIME < 5.0" | bc -l) )); then
            print_pass "Load time is good (<5s)"
        else
            print_warn "Load time is slow (${LOAD_TIME}s)" "Expected <5s for 7B models"
        fi
    fi

    # Test inference
    print_section "Inference Test"

    INFERENCE_TEST=$("$VENV_PATH/bin/python3" << EOF
import time
from mlx_lm import load, generate

model_name = "$TEST_MODEL"
test_prompt = "Write a Python hello world"

try:
    print("Loading model...", flush=True)
    model, tokenizer = load(model_name)

    print("Generating text...", flush=True)
    start = time.time()
    response = generate(
        model,
        tokenizer,
        prompt=test_prompt,
        max_tokens=50,
        verbose=False
    )
    inference_time = time.time() - start

    # Count tokens (approximate)
    tokens = len(response.split())
    tok_per_sec = tokens / inference_time if inference_time > 0 else 0

    print(f"INFERENCE_TIME:{inference_time:.3f}")
    print(f"TOKENS:{tokens}")
    print(f"TOK_PER_SEC:{tok_per_sec:.1f}")
    print("SUCCESS")
except Exception as e:
    print(f"ERROR:{e}")
EOF
)

    if echo "$INFERENCE_TEST" | grep -q "ERROR:"; then
        ERROR_MSG=$(echo "$INFERENCE_TEST" | grep "ERROR:" | cut -d: -f2-)
        print_fail "Inference failed: $ERROR_MSG"
    elif echo "$INFERENCE_TEST" | grep -q "SUCCESS"; then
        INF_TIME=$(echo "$INFERENCE_TEST" | grep "INFERENCE_TIME:" | cut -d: -f2)
        TOKENS=$(echo "$INFERENCE_TEST" | grep "TOKENS:" | cut -d: -f2)
        TOK_PER_SEC=$(echo "$INFERENCE_TEST" | grep "TOK_PER_SEC:" | cut -d: -f2)

        print_pass "Inference successful"
        print_value "Time" "${INF_TIME}s"
        print_value "Tokens generated" "$TOKENS"
        print_value "Speed" "${TOK_PER_SEC} tok/sec"

        # Performance check
        if (( $(echo "$TOK_PER_SEC > 50" | bc -l) )); then
            print_pass "Inference speed is excellent (>50 tok/sec)"
        elif (( $(echo "$TOK_PER_SEC > 20" | bc -l) )); then
            print_pass "Inference speed is good (>20 tok/sec)"
        else
            print_warn "Inference speed is slow (${TOK_PER_SEC} tok/sec)" "Expected >20 tok/sec"
        fi
    fi
}

###############################################################################
# Test 7: Memory Usage
###############################################################################

test_memory_usage() {
    print_header "7. MEMORY USAGE"

    print_section "System Memory"

    # Get memory info
    MEM_INFO=$(vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%-16s % 16.2f Mi\n", "$1:", $2 * $size / 1048576);')

    FREE_PAGES=$(vm_stat | grep "Pages free" | awk '{print $3}' | tr -d '.')
    INACTIVE_PAGES=$(vm_stat | grep "Pages inactive" | awk '{print $3}' | tr -d '.')
    PAGE_SIZE=$(vm_stat | grep "page size" | awk '{print $8}')

    FREE_GB=$(echo "scale=2; ($FREE_PAGES + $INACTIVE_PAGES) * $PAGE_SIZE / 1024 / 1024 / 1024" | bc)

    print_value "Free memory (approx)" "${FREE_GB}GB"

    if (( $(echo "$FREE_GB > 8" | bc -l) )); then
        print_pass "Sufficient free memory for MLX models"
    elif (( $(echo "$FREE_GB > 4" | bc -l) )); then
        print_warn "Low free memory: ${FREE_GB}GB" "Close other apps for best performance"
    else
        print_fail "Very low free memory: ${FREE_GB}GB" "MLX may fail to load models"
    fi

    print_section "Memory Pressure"

    # Check memory pressure
    MEM_PRESSURE=$(memory_pressure 2>&1)

    if echo "$MEM_PRESSURE" | grep -q "normal"; then
        print_pass "Memory pressure is normal"
    elif echo "$MEM_PRESSURE" | grep -q "warn"; then
        print_warn "Memory pressure is elevated" "Close unused applications"
    elif echo "$MEM_PRESSURE" | grep -q "critical"; then
        print_fail "Memory pressure is critical" "Free up memory before using MLX"
    else
        print_info "Memory pressure status: unknown"
    fi
}

###############################################################################
# Summary Report
###############################################################################

print_summary() {
    print_header "HEALTH CHECK SUMMARY"

    echo -e "\n${BOLD}Test Results:${RESET}"
    echo -e "  ${GREEN}Passed:${RESET}  $PASSED_TESTS"
    echo -e "  ${YELLOW}Warnings:${RESET} $WARNING_TESTS"
    echo -e "  ${RED}Failed:${RESET}  $FAILED_TESTS"
    echo -e "  ${CYAN}Total:${RESET}   $TOTAL_TESTS"

    # Overall status
    echo -e "\n${BOLD}Overall Status:${RESET}"
    if [ "$FAILED_TESTS" -eq 0 ] && [ "$WARNING_TESTS" -eq 0 ]; then
        echo -e "  ${GREEN}${BOLD}${ROCKET} EXCELLENT${RESET} - Your MLX setup is perfect!"
        echo -e "  ${GREEN}All systems operational. Ready for production use.${RESET}"
    elif [ "$FAILED_TESTS" -eq 0 ]; then
        echo -e "  ${GREEN}${BOLD}${CHECK} GOOD${RESET} - MLX is ready to use"
        echo -e "  ${YELLOW}Minor warnings present. Review recommendations below.${RESET}"
    elif [ "$FAILED_TESTS" -le 2 ]; then
        echo -e "  ${YELLOW}${BOLD}${WARN} NEEDS ATTENTION${RESET} - Some issues detected"
        echo -e "  ${YELLOW}MLX may work with limitations. Fix critical issues.${RESET}"
    else
        echo -e "  ${RED}${BOLD}${CROSS} NOT READY${RESET} - Multiple failures detected"
        echo -e "  ${RED}MLX will not work properly. Fix issues below.${RESET}"
    fi

    # Errors
    if [ ${#ERRORS[@]} -gt 0 ]; then
        echo -e "\n${RED}${BOLD}Critical Issues:${RESET}"
        for error in "${ERRORS[@]}"; do
            echo -e "  ${RED}•${RESET} $error"
        done
    fi

    # Warnings
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo -e "\n${YELLOW}${BOLD}Warnings:${RESET}"
        for warning in "${WARNINGS[@]}"; do
            echo -e "  ${YELLOW}•${RESET} $warning"
        done
    fi

    # Recommendations
    echo -e "\n${CYAN}${BOLD}Recommendations:${RESET}"

    if [ "$FAILED_TESTS" -gt 0 ]; then
        echo -e "  ${CYAN}1.${RESET} Fix all critical failures listed above"
        echo -e "  ${CYAN}2.${RESET} Refer to OLLAMA-TO-MLX-MIGRATION-GUIDE.md for help"
        echo -e "  ${CYAN}3.${RESET} Run this script again after fixes"
    elif [ "$WARNING_TESTS" -gt 0 ]; then
        echo -e "  ${CYAN}1.${RESET} Review warnings for optimal performance"
        echo -e "  ${CYAN}2.${RESET} Consider downloading recommended models"
        echo -e "  ${CYAN}3.${RESET} Run test-mlx-models.py for performance benchmarks"
    else
        echo -e "  ${CYAN}1.${RESET} Run test-mlx-models.py to benchmark performance"
        echo -e "  ${CYAN}2.${RESET} Try python3 ai-router-mlx.py for interactive use"
        echo -e "  ${CYAN}3.${RESET} Read OLLAMA-TO-MLX-MIGRATION-GUIDE.md for tips"
    fi

    # Next steps
    echo -e "\n${CYAN}${BOLD}Next Steps:${RESET}"
    echo -e "  ${DIM}# Benchmark performance${RESET}"
    echo -e "  ${WHITE}python3 test-mlx-models.py${RESET}"
    echo -e ""
    echo -e "  ${DIM}# Launch AI Router MLX${RESET}"
    echo -e "  ${WHITE}python3 ai-router-mlx.py${RESET}"
    echo -e ""
    echo -e "  ${DIM}# Quick model test${RESET}"
    echo -e "  ${WHITE}source ~/workspace/venv-mlx/bin/activate${RESET}"
    echo -e "  ${WHITE}mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit${RESET}"

    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    print_banner

    test_system_requirements
    test_python_environment
    test_mlx_installation
    test_metal_gpu
    test_available_models
    test_model_loading
    test_memory_usage

    print_summary

    # Exit code
    if [ "$FAILED_TESTS" -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main
main "$@"
