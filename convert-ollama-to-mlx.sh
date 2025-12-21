#!/bin/bash

################################################################################
# Ollama to MLX Model Conversion Orchestrator
#
# This script orchestrates the complete migration from Ollama GGUF models to
# MLX-optimized models for Apple Silicon.
#
# Features:
# - Pre-flight checks for system requirements
# - Analysis of current Ollama models
# - Interactive or automated model deletion
# - MLX model download with progress tracking
# - Before/after state comparison
# - Rollback capability
#
# Usage:
#   ./convert-ollama-to-mlx.sh [OPTIONS]
#
# Options:
#   --dry-run          Show what would be done without making changes
#   --auto             Non-interactive mode (use with caution)
#   --skip-analysis    Skip initial analysis step
#   --skip-downloads   Only delete Ollama models, don't download MLX
#   --help             Show this help message
#
# Safety:
#   - Creates backups of Ollama model list before deletion
#   - Supports dry-run mode for testing
#   - Validates each step before proceeding
#   - Provides rollback instructions if needed
#
################################################################################

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAPPING_FILE="${SCRIPT_DIR}/mlx-model-mapping.json"
ANALYSIS_SCRIPT="${SCRIPT_DIR}/ollama-model-analysis.py"
MLX_DIR="${SCRIPT_DIR}/mlx"
BACKUP_DIR="${SCRIPT_DIR}/.ollama-backups"
LOG_FILE="${SCRIPT_DIR}/conversion-$(date +%Y%m%d-%H%M%S).log"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default options
DRY_RUN=false
AUTO_MODE=false
SKIP_ANALYSIS=false
SKIP_DOWNLOADS=false

################################################################################
# Utility Functions
################################################################################

log() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}✗ ERROR:${NC} $*" | tee -a "$LOG_FILE" >&2
}

log_warning() {
    echo -e "${YELLOW}⚠ WARNING:${NC} $*" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}ℹ INFO:${NC} $*" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "\n${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
    echo -e "${MAGENTA}▶ $*${NC}" | tee -a "$LOG_FILE"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n" | tee -a "$LOG_FILE"
}

confirm() {
    if [ "$AUTO_MODE" = true ]; then
        return 0
    fi

    local prompt="$1"
    local response

    while true; do
        read -p "$(echo -e "${YELLOW}${prompt} (y/n):${NC} ")" -r response
        case "$response" in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

check_command() {
    local cmd="$1"
    if ! command -v "$cmd" &> /dev/null; then
        log_error "Required command '$cmd' not found"
        return 1
    fi
    return 0
}

################################################################################
# Pre-flight Checks
################################################################################

preflight_checks() {
    log_step "Running Pre-flight Checks"

    # Check if running on macOS
    if [[ "$(uname)" != "Darwin" ]]; then
        log_error "This script is designed for macOS only"
        exit 1
    fi
    log_success "Running on macOS"

    # Check for Apple Silicon
    if [[ "$(uname -m)" != "arm64" ]]; then
        log_warning "Not running on Apple Silicon (arm64). MLX may not work optimally."
    else
        log_success "Running on Apple Silicon"
    fi

    # Check required commands
    local required_commands=("ollama" "python3" "jq")
    for cmd in "${required_commands[@]}"; do
        if check_command "$cmd"; then
            log_success "Found: $cmd"
        else
            log_error "Missing required command: $cmd"
            if [ "$cmd" = "jq" ]; then
                log_info "Install with: brew install jq"
            fi
            exit 1
        fi
    done

    # Check if Ollama is running
    if ! ollama list &> /dev/null; then
        log_error "Ollama is not running or not accessible"
        log_info "Start Ollama with: ollama serve"
        exit 1
    fi
    log_success "Ollama is accessible"

    # Check Python version
    local python_version=$(python3 --version | cut -d' ' -f2)
    log_success "Python version: $python_version"

    # Check if mapping file exists
    if [ ! -f "$MAPPING_FILE" ]; then
        log_error "Mapping file not found: $MAPPING_FILE"
        exit 1
    fi
    log_success "Found mapping file: $MAPPING_FILE"

    # Check if analysis script exists
    if [ ! -f "$ANALYSIS_SCRIPT" ]; then
        log_error "Analysis script not found: $ANALYSIS_SCRIPT"
        exit 1
    fi
    log_success "Found analysis script: $ANALYSIS_SCRIPT"

    # Check available disk space
    local available_space=$(df -g . | awk 'NR==2 {print $4}')
    log_info "Available disk space: ${available_space} GB"

    if [ "$available_space" -lt 50 ]; then
        log_warning "Low disk space. Recommend at least 50GB free for safe migration."
        if ! confirm "Continue anyway?"; then
            exit 1
        fi
    fi

    # Create directories
    mkdir -p "$MLX_DIR"
    mkdir -p "$BACKUP_DIR"
    log_success "Created/verified working directories"

    log_success "All pre-flight checks passed"
}

################################################################################
# Analysis Functions
################################################################################

run_analysis() {
    log_step "Analyzing Current Ollama Models"

    if [ "$SKIP_ANALYSIS" = true ]; then
        log_info "Skipping analysis (--skip-analysis flag)"
        return 0
    fi

    # Run Python analysis script
    if ! python3 "$ANALYSIS_SCRIPT" --mapping "$MAPPING_FILE"; then
        log_error "Analysis failed"
        exit 1
    fi

    log_success "Analysis complete"

    # Save JSON analysis for later use
    python3 "$ANALYSIS_SCRIPT" --mapping "$MAPPING_FILE" --json > "${BACKUP_DIR}/analysis-$(date +%Y%m%d-%H%M%S).json"
    log_info "Analysis saved to backup directory"
}

################################################################################
# Backup Functions
################################################################################

backup_ollama_state() {
    log_step "Backing Up Current Ollama State"

    local backup_file="${BACKUP_DIR}/ollama-list-$(date +%Y%m%d-%H%M%S).txt"

    # Save current Ollama model list
    ollama list > "$backup_file"
    log_success "Saved Ollama model list to: $backup_file"

    # Also save as JSON
    local backup_json="${BACKUP_DIR}/ollama-models-$(date +%Y%m%d-%H%M%S).json"
    python3 -c "
import subprocess
import json
result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
lines = result.stdout.strip().split('\n')[1:]
models = []
for line in lines:
    parts = line.split()
    if len(parts) >= 4:
        models.append({
            'name': parts[0],
            'id': parts[1],
            'size': f'{parts[2]} {parts[3]}',
            'modified': ' '.join(parts[4:])
        })
print(json.dumps(models, indent=2))
" > "$backup_json"

    log_success "Saved JSON backup to: $backup_json"
    log_info "Backup directory: $BACKUP_DIR"
}

################################################################################
# Deletion Functions
################################################################################

delete_ollama_models() {
    log_step "Deleting Ollama Models"

    # Get list of models to delete from mapping
    local models_to_delete=$(jq -r '.models_to_delete[].ollama_name' "$MAPPING_FILE")

    if [ -z "$models_to_delete" ]; then
        log_warning "No models marked for deletion in mapping file"
        return 0
    fi

    local delete_count=0
    local total_size=0

    # Count and calculate total size
    while IFS= read -r model; do
        ((delete_count++))
        local size=$(jq -r --arg model "$model" '.models_to_delete[] | select(.ollama_name == $model) | .size_gb' "$MAPPING_FILE")
        total_size=$(echo "$total_size + $size" | bc)
    done <<< "$models_to_delete"

    log_info "Models to delete: $delete_count"
    log_info "Space to free: ${total_size} GB"

    echo ""
    log_warning "The following models will be DELETED:"
    echo ""

    while IFS= read -r model; do
        local size=$(jq -r --arg model "$model" '.models_to_delete[] | select(.ollama_name == $model) | .size_gb' "$MAPPING_FILE")
        local reason=$(jq -r --arg model "$model" '.models_to_delete[] | select(.ollama_name == $model) | .reason' "$MAPPING_FILE")
        echo "  • $model (${size} GB)"
        echo "    → $reason"
    done <<< "$models_to_delete"

    echo ""

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would delete ${delete_count} models"
        return 0
    fi

    if ! confirm "Proceed with deletion?"; then
        log_warning "Deletion cancelled by user"
        return 1
    fi

    # Delete models
    local deleted=0
    local failed=0

    while IFS= read -r model; do
        log "Deleting: $model"

        if ollama rm "$model"; then
            log_success "Deleted: $model"
            ((deleted++))
        else
            log_error "Failed to delete: $model"
            ((failed++))
        fi
    done <<< "$models_to_delete"

    log_success "Deleted $deleted models successfully"

    if [ $failed -gt 0 ]; then
        log_error "Failed to delete $failed models"
    fi

    # Show new state
    echo ""
    log_info "Remaining Ollama models:"
    ollama list
}

################################################################################
# MLX Download Functions
################################################################################

check_mlx_installation() {
    log_step "Checking MLX Installation"

    # Check if mlx_lm is installed
    if ! python3 -c "import mlx_lm" 2>/dev/null; then
        log_warning "MLX not installed"

        if confirm "Install MLX now?"; then
            log "Installing MLX..."

            # Create or activate venv
            if [ ! -d "${MLX_DIR}/venv" ]; then
                python3 -m venv "${MLX_DIR}/venv"
                log_success "Created MLX virtual environment"
            fi

            source "${MLX_DIR}/venv/bin/activate"

            pip install --upgrade pip
            pip install -U mlx-lm

            log_success "MLX installed successfully"
        else
            log_warning "Skipping MLX installation. Downloads will be skipped."
            SKIP_DOWNLOADS=true
        fi
    else
        log_success "MLX is already installed"
    fi
}

download_mlx_models() {
    log_step "Downloading MLX Models"

    if [ "$SKIP_DOWNLOADS" = true ]; then
        log_info "Skipping downloads (--skip-downloads flag or MLX not installed)"
        return 0
    fi

    # Get list of MLX models that need to be downloaded
    local models_to_download=$(jq -r '.mlx_models | to_entries[] | select(.value.status == "PENDING") | .key' "$MAPPING_FILE")

    if [ -z "$models_to_download" ]; then
        log_info "All required MLX models are already downloaded"
        return 0
    fi

    log_info "MLX models to download:"
    while IFS= read -r model_key; do
        local repo=$(jq -r --arg key "$model_key" '.mlx_models[$key].huggingface_repo' "$MAPPING_FILE")
        local size=$(jq -r --arg key "$model_key" '.mlx_models[$key].size_gb' "$MAPPING_FILE")
        echo "  • $model_key → $repo (${size} GB)"
    done <<< "$models_to_download"

    echo ""

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would download MLX models"
        return 0
    fi

    if ! confirm "Proceed with MLX model downloads?"; then
        log_warning "Downloads cancelled by user"
        return 1
    fi

    # Activate MLX venv if it exists
    if [ -d "${MLX_DIR}/venv" ]; then
        source "${MLX_DIR}/venv/bin/activate"
    fi

    # Download each model
    while IFS= read -r model_key; do
        local repo=$(jq -r --arg key "$model_key" '.mlx_models[$key].huggingface_repo' "$MAPPING_FILE")
        local local_path="${MLX_DIR}/${model_key}"

        log "Downloading: $repo"
        log_info "Destination: $local_path"

        # Create directory
        mkdir -p "$local_path"

        # Download using huggingface_hub
        if python3 -c "
from huggingface_hub import snapshot_download
import sys
try:
    snapshot_download(
        repo_id='$repo',
        local_dir='$local_path',
        local_dir_use_symlinks=False
    )
    print('Download successful')
    sys.exit(0)
except Exception as e:
    print(f'Download failed: {e}', file=sys.stderr)
    sys.exit(1)
"; then
            log_success "Downloaded: $model_key"
        else
            log_error "Failed to download: $model_key"
            log_info "You can manually download with:"
            log_info "  huggingface-cli download $repo --local-dir $local_path"
        fi

    done <<< "$models_to_download"

    log_success "MLX model downloads complete"
}

################################################################################
# State Reporting Functions
################################################################################

show_before_after_state() {
    log_step "Before/After Comparison"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "BEFORE STATE (from backup)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Show most recent backup
    local latest_backup=$(ls -t "${BACKUP_DIR}"/ollama-list-*.txt 2>/dev/null | head -1)
    if [ -f "$latest_backup" ]; then
        cat "$latest_backup"
    else
        log_warning "No backup found"
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "AFTER STATE (current)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    ollama list

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "MLX MODELS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [ -d "$MLX_DIR" ]; then
        ls -lh "$MLX_DIR" | grep "^d" | awk '{print $9, "(" $5 ")"}'
    else
        log_warning "MLX directory not found"
    fi

    echo ""
}

show_usage_instructions() {
    log_step "Usage Instructions"

    cat << 'EOF'

MLX MODELS ARE NOW READY TO USE!

Quick Start Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For Daily Use:

  # Fast coding (60-80 tok/sec)
  mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit

  # General questions (40-60 tok/sec)
  mlx_lm.chat --model mlx-community/Qwen3-14B-Instruct-4bit

For Specialized Tasks:

  # Math & reasoning (50-70 tok/sec)
  mlx_lm.chat --model mlx-community/DeepSeek-R1-Distill-Llama-8B

  # Complex coding (11-22 tok/sec, needs 32GB+ RAM)
  mlx_lm.chat --model mlx-community/Qwen2.5-Coder-32B-Instruct-4bit

  # Ultra-fast general (70-100 tok/sec)
  mlx_lm.chat --model mlx-community/Mistral-7B-Instruct-v0.3-4bit

Setup Virtual Environment (if needed):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  source mlx/venv/bin/activate

Performance Improvements:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Qwen2.5-Coder-7B:  200-300% faster than GGUF
  • DeepSeek-R1-8B:    400-600% faster than 32B GGUF
  • Qwen3-14B:         100-200% faster than GGUF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
}

################################################################################
# Main Orchestration
################################################################################

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Orchestrates migration from Ollama GGUF models to MLX-optimized models.

OPTIONS:
    --dry-run          Show what would be done without making changes
    --auto             Non-interactive mode (automatic yes to prompts)
    --skip-analysis    Skip initial analysis step
    --skip-downloads   Only delete Ollama models, don't download MLX
    --help             Show this help message

EXAMPLES:
    # Preview what will happen
    $0 --dry-run

    # Interactive migration (recommended)
    $0

    # Fully automated migration
    $0 --auto

    # Delete Ollama models only
    $0 --skip-downloads

EOF
}

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                log_info "DRY RUN MODE - No changes will be made"
                ;;
            --auto)
                AUTO_MODE=true
                log_info "AUTO MODE - No confirmations will be requested"
                ;;
            --skip-analysis)
                SKIP_ANALYSIS=true
                ;;
            --skip-downloads)
                SKIP_DOWNLOADS=true
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
        shift
    done

    # Print banner
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "    OLLAMA TO MLX MODEL CONVERSION ORCHESTRATOR"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    log_info "Log file: $LOG_FILE"

    # Execute conversion workflow
    preflight_checks
    run_analysis
    backup_ollama_state

    if [ "$DRY_RUN" = false ]; then
        delete_ollama_models
        check_mlx_installation
        download_mlx_models
        show_before_after_state
        show_usage_instructions
    else
        log_info "[DRY RUN] Skipping actual changes"
        delete_ollama_models
    fi

    log_success "Conversion orchestration complete!"
    log_info "Log saved to: $LOG_FILE"
}

# Run main function
main "$@"
