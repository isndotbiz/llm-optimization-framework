#!/bin/bash
################################################################################
# MLX Setup Script for MacBook (M1/M2/M3/M4)
#
# This script automates the complete MLX installation process:
# - Creates Python virtual environment at ~/venv-mlx
# - Installs MLX, mlx-lm, and all dependencies
# - Sets up environment variables and shell aliases
# - Validates the installation with GPU/Metal support
# - Creates helper functions for easy use
#
# Usage:
#   chmod +x setup-mlx-macbook.sh
#   ./setup-mlx-macbook.sh
#
# Safe to run multiple times (idempotent)
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly RESET='\033[0m'

# Configuration
readonly VENV_PATH="${HOME}/venv-mlx"
readonly WORKSPACE_PATH="${HOME}/workspace"
readonly MLX_MODELS_PATH="${WORKSPACE_PATH}/mlx"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PYTHON_SETUP_SCRIPT="${SCRIPT_DIR}/setup_mlx_environment.py"

################################################################################
# Utility Functions
################################################################################

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════════${RESET}"
    echo -e "${BOLD}${BLUE}  $1${RESET}"
    echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════════${RESET}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${RESET} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${RESET} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${RESET} $1"
}

print_error() {
    echo -e "${RED}✗${RESET} $1" >&2
}

print_step() {
    echo -e "\n${BOLD}→ $1${RESET}"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

################################################################################
# Pre-flight Checks
################################################################################

check_prerequisites() {
    print_header "Pre-flight Checks"

    # Check if running on macOS
    if [[ "$(uname -s)" != "Darwin" ]]; then
        print_error "This script is designed for macOS only"
        print_info "Detected OS: $(uname -s)"
        exit 1
    fi
    print_success "Running on macOS"

    # Check for Apple Silicon
    local arch=$(uname -m)
    if [[ "$arch" != "arm64" ]]; then
        print_warning "Not running on Apple Silicon (detected: $arch)"
        print_warning "MLX performance is optimized for M1/M2/M3/M4 chips"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "Running on Apple Silicon ($arch)"
    fi

    # Check Python version
    if ! command_exists python3; then
        print_error "python3 not found. Please install Python 3.9 or higher"
        print_info "Install via: brew install python@3.11"
        exit 1
    fi

    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python found: $python_version"

    # Verify Python 3.9+
    local major=$(echo "$python_version" | cut -d. -f1)
    local minor=$(echo "$python_version" | cut -d. -f2)
    if [[ "$major" -lt 3 ]] || [[ "$major" -eq 3 && "$minor" -lt 9 ]]; then
        print_error "Python 3.9+ required (found: $python_version)"
        exit 1
    fi

    # Check available disk space (need at least 10GB)
    local available_gb=$(df -g "$HOME" | tail -1 | awk '{print $4}')
    if [[ "$available_gb" -lt 10 ]]; then
        print_warning "Low disk space: ${available_gb}GB available"
        print_warning "Recommended: 10GB+ for models and dependencies"
    else
        print_success "Sufficient disk space: ${available_gb}GB available"
    fi

    # Check memory
    local total_mem_gb=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    print_info "Total RAM: ${total_mem_gb}GB"
    if [[ "$total_mem_gb" -lt 16 ]]; then
        print_warning "16GB+ RAM recommended for optimal performance"
    fi
}

################################################################################
# Virtual Environment Setup
################################################################################

setup_virtual_environment() {
    print_header "Setting Up Python Virtual Environment"

    if [[ -d "$VENV_PATH" ]]; then
        print_warning "Virtual environment already exists at $VENV_PATH"
        read -p "Recreate it? This will delete existing environment (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_step "Removing existing virtual environment"
            rm -rf "$VENV_PATH"
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi

    print_step "Creating virtual environment at $VENV_PATH"
    python3 -m venv "$VENV_PATH"
    print_success "Virtual environment created"

    print_step "Activating virtual environment"
    source "$VENV_PATH/bin/activate"
    print_success "Virtual environment activated"

    print_step "Upgrading pip"
    pip install --upgrade pip --quiet
    print_success "pip upgraded to $(pip --version | awk '{print $2}')"
}

################################################################################
# MLX Installation
################################################################################

install_mlx_packages() {
    print_header "Installing MLX and Dependencies"

    # Ensure venv is activated
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        print_step "Activating virtual environment"
        source "$VENV_PATH/bin/activate"
    fi

    print_step "Installing MLX core packages"
    pip install --upgrade mlx mlx-lm
    print_success "MLX packages installed"

    print_step "Installing additional dependencies"
    # Install common dependencies for AI router scripts
    pip install --upgrade \
        numpy \
        transformers \
        huggingface-hub \
        sentencepiece \
        tiktoken
    print_success "Dependencies installed"

    print_step "Verifying installations"
    python3 -c "import mlx.core as mx; print(f'MLX version: {mx.__version__}')"
    python3 -c "import mlx_lm; print('mlx-lm installed successfully')"
    print_success "All packages verified"
}

################################################################################
# Directory Structure
################################################################################

create_directory_structure() {
    print_header "Setting Up Directory Structure"

    print_step "Creating workspace directories"
    mkdir -p "$WORKSPACE_PATH"
    mkdir -p "$MLX_MODELS_PATH"

    print_success "Created: $WORKSPACE_PATH"
    print_success "Created: $MLX_MODELS_PATH"

    print_info "Models should be placed in: $MLX_MODELS_PATH"
}

################################################################################
# Shell Configuration
################################################################################

configure_shell() {
    print_header "Configuring Shell Environment"

    # Detect shell
    local shell_config=""
    if [[ -n "${ZSH_VERSION:-}" ]] || [[ "$SHELL" == *"zsh"* ]]; then
        shell_config="${HOME}/.zshrc"
    elif [[ -n "${BASH_VERSION:-}" ]] || [[ "$SHELL" == *"bash"* ]]; then
        shell_config="${HOME}/.bashrc"
    else
        print_warning "Unknown shell. Skipping shell configuration."
        return 0
    fi

    print_step "Configuring $shell_config"

    # Backup existing config
    if [[ -f "$shell_config" ]]; then
        cp "$shell_config" "${shell_config}.backup.$(date +%Y%m%d_%H%M%S)"
        print_info "Backed up existing configuration"
    fi

    # Check if MLX config already exists
    if grep -q "# MLX Environment Configuration" "$shell_config" 2>/dev/null; then
        print_warning "MLX configuration already exists in $shell_config"
        read -p "Update it? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Remove old configuration
            sed -i.bak '/# MLX Environment Configuration/,/# End MLX Configuration/d' "$shell_config"
            print_info "Removed old configuration"
        else
            print_info "Skipping shell configuration update"
            return 0
        fi
    fi

    # Add MLX configuration
    cat >> "$shell_config" << 'EOF'

# MLX Environment Configuration
# Auto-generated by setup-mlx-macbook.sh

# MLX virtual environment path
export MLX_VENV_PATH="${HOME}/venv-mlx"
export MLX_MODELS_PATH="${HOME}/workspace/mlx"

# Activate MLX environment
alias mlx-activate='source ${MLX_VENV_PATH}/bin/activate'

# Quick MLX model commands
alias mlx-qwen7b='mlx_lm.generate --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit'
alias mlx-qwen32b='mlx_lm.generate --model mlx-community/Qwen2.5-Coder-32B-Instruct-4bit'
alias mlx-deepseek='mlx_lm.generate --model mlx-community/DeepSeek-R1-Distill-Llama-8B'
alias mlx-phi4='mlx_lm.generate --model mlx-community/phi-4-4bit'

# Interactive chat sessions
alias mlx-chat-qwen7b='mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit'
alias mlx-chat-qwen32b='mlx_lm.chat --model mlx-community/Qwen2.5-Coder-32B-Instruct-4bit'
alias mlx-chat-deepseek='mlx_lm.chat --model mlx-community/DeepSeek-R1-Distill-Llama-8B'
alias mlx-chat-phi4='mlx_lm.chat --model mlx-community/phi-4-4bit'

# Helper function to list available MLX models
mlx-models() {
    echo "Available MLX Models:"
    echo "  qwen7b     - Qwen2.5 Coder 7B (Fast, 60-80 tok/sec)"
    echo "  qwen32b    - Qwen2.5 Coder 32B (Best quality, 11-22 tok/sec)"
    echo "  deepseek   - DeepSeek-R1 8B (Reasoning, 50-70 tok/sec)"
    echo "  phi4       - Phi-4 14B (Math/code, 40-60 tok/sec)"
    echo ""
    echo "Usage: mlx-chat-<model> or mlx-<model> --prompt 'Your prompt'"
}

# Helper function to check MLX status
mlx-status() {
    echo "MLX Environment Status:"
    echo "  Virtual Env: ${MLX_VENV_PATH}"
    echo "  Models Path: ${MLX_MODELS_PATH}"
    echo ""
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        echo "  ✓ Virtual environment activated"
        echo "  Python: $(python --version)"
        python -c "import mlx.core as mx; print(f'  MLX Version: {mx.__version__}')" 2>/dev/null || echo "  ✗ MLX not installed"
    else
        echo "  ✗ Virtual environment not activated"
        echo "  Run: mlx-activate"
    fi
}

# Helper function to validate MLX installation
mlx-validate() {
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        echo "Activating MLX environment..."
        source "${MLX_VENV_PATH}/bin/activate"
    fi

    python3 "${HOME}/workspace/llm-optimization-framework/setup_mlx_environment.py" --validate
}

# End MLX Configuration
EOF

    print_success "Shell configuration updated"
    print_info "Reload your shell or run: source $shell_config"
}

################################################################################
# Validation
################################################################################

run_validation() {
    print_header "Validating MLX Installation"

    # Ensure venv is activated
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        source "$VENV_PATH/bin/activate"
    fi

    if [[ -f "$PYTHON_SETUP_SCRIPT" ]]; then
        print_step "Running Python validation script"
        python3 "$PYTHON_SETUP_SCRIPT" --validate
    else
        print_warning "Python setup script not found at $PYTHON_SETUP_SCRIPT"
        print_info "Running basic validation"

        print_step "Testing MLX import"
        python3 -c "import mlx.core as mx; print(f'MLX Version: {mx.__version__}')"

        print_step "Testing Metal backend"
        python3 -c "import mlx.core as mx; print(f'Default device: {mx.default_device()}')"

        print_step "Testing mlx-lm"
        python3 -c "import mlx_lm; print('mlx-lm: OK')"

        print_success "Basic validation passed"
    fi
}

################################################################################
# Summary
################################################################################

print_summary() {
    print_header "Installation Complete!"

    echo -e "${BOLD}Next Steps:${RESET}"
    echo ""
    echo "1. Activate the MLX environment:"
    echo -e "   ${CYAN}source ~/venv-mlx/bin/activate${RESET}"
    echo ""
    echo "2. Or reload your shell to use aliases:"
    echo -e "   ${CYAN}source ~/.zshrc${RESET}  # or ~/.bashrc"
    echo -e "   ${CYAN}mlx-activate${RESET}"
    echo ""
    echo "3. Test the installation:"
    echo -e "   ${CYAN}mlx-status${RESET}"
    echo -e "   ${CYAN}mlx-validate${RESET}"
    echo ""
    echo "4. Start using MLX models:"
    echo -e "   ${CYAN}mlx-chat-qwen7b${RESET}  # Fast coding"
    echo -e "   ${CYAN}mlx-models${RESET}        # List all available models"
    echo ""
    echo -e "${BOLD}Quick Commands:${RESET}"
    echo -e "   ${CYAN}mlx-activate${RESET}     - Activate MLX environment"
    echo -e "   ${CYAN}mlx-models${RESET}       - List available models"
    echo -e "   ${CYAN}mlx-status${RESET}       - Check installation status"
    echo -e "   ${CYAN}mlx-validate${RESET}     - Run full validation"
    echo ""
    echo -e "${BOLD}Model Paths:${RESET}"
    echo -e "   Virtual Env: ${GREEN}${VENV_PATH}${RESET}"
    echo -e "   Models:      ${GREEN}${MLX_MODELS_PATH}${RESET}"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    clear
    print_header "MLX Setup for MacBook (M1/M2/M3/M4)"

    echo "This script will:"
    echo "  • Create Python virtual environment at ~/venv-mlx"
    echo "  • Install MLX and mlx-lm packages"
    echo "  • Set up workspace directories"
    echo "  • Configure shell aliases and helpers"
    echo "  • Validate the installation"
    echo ""

    read -p "Continue? (Y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi

    # Run installation steps
    check_prerequisites
    setup_virtual_environment
    install_mlx_packages
    create_directory_structure
    configure_shell
    run_validation
    print_summary

    print_success "Setup completed successfully!"
}

# Run main function
main "$@"
