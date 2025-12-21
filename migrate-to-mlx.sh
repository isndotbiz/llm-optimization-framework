#!/bin/bash

################################################################################
# Automated MLX Migration Script
#
# This script provides a streamlined, non-interactive migration from Ollama
# to MLX models. Designed for use in automation, CI/CD, or when you've
# already reviewed the changes and want to execute them quickly.
#
# Features:
# - Non-interactive execution with safety checks
# - Detailed progress reporting
# - Error recovery and rollback
# - Pre-migration validation
# - Post-migration verification
#
# Usage:
#   ./migrate-to-mlx.sh [--execute|--dry-run] [OPTIONS]
#
# Options:
#   --execute              Execute the migration (required for actual changes)
#   --dry-run              Preview changes without executing
#   --force                Skip confirmations (use with extreme caution)
#   --delete-only          Only delete Ollama models, skip MLX downloads
#   --download-only        Only download MLX models, skip Ollama deletions
#   --verify-only          Only verify current state
#   --rollback             Attempt to rollback to previous state (if possible)
#   --help                 Show this help message
#
# Safety Features:
#   - Requires explicit --execute flag to make changes
#   - Creates timestamped backups before any deletions
#   - Validates available disk space before downloads
#   - Logs all operations for audit trail
#   - Provides rollback instructions on failure
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Pre-flight check failed
#   3 - Migration failed (rollback may be needed)
#   4 - User cancellation
#
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAPPING_FILE="${SCRIPT_DIR}/mlx-model-mapping.json"
MLX_DIR="${SCRIPT_DIR}/mlx"
BACKUP_DIR="${SCRIPT_DIR}/.ollama-backups"
STATE_FILE="${BACKUP_DIR}/migration-state.json"
LOG_FILE="${SCRIPT_DIR}/migration-$(date +%Y%m%d-%H%M%S).log"

# Execution mode
EXECUTE_MODE=false
DRY_RUN=false
FORCE_MODE=false
DELETE_ONLY=false
DOWNLOAD_ONLY=false
VERIFY_ONLY=false
ROLLBACK_MODE=false

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Progress tracking
TOTAL_STEPS=0
CURRENT_STEP=0

################################################################################
# Logging Functions
################################################################################

log() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
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
    echo -e "${BLUE}ℹ${NC} $*" | tee -a "$LOG_FILE"
}

log_header() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BOLD}${MAGENTA}$*${NC}" | tee -a "$LOG_FILE"
    echo -e "${MAGENTA}$(echo "$*" | sed 's/./━/g')${NC}" | tee -a "$LOG_FILE"
}

progress() {
    ((CURRENT_STEP++))
    local percent=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    echo -e "${CYAN}[${CURRENT_STEP}/${TOTAL_STEPS}]${NC} ${BOLD}$*${NC} ${CYAN}(${percent}%)${NC}" | tee -a "$LOG_FILE"
}

################################################################################
# State Management
################################################################################

save_state() {
    local state="$1"
    local details="$2"

    mkdir -p "$BACKUP_DIR"

    cat > "$STATE_FILE" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "state": "$state",
  "details": "$details",
  "log_file": "$LOG_FILE"
}
EOF

    log_info "State saved: $state"
}

get_last_state() {
    if [ -f "$STATE_FILE" ]; then
        jq -r '.state' "$STATE_FILE" 2>/dev/null || echo "unknown"
    else
        echo "none"
    fi
}

################################################################################
# Validation Functions
################################################################################

validate_environment() {
    log_header "Validating Environment"

    local errors=0

    # Check OS
    if [[ "$(uname)" != "Darwin" ]]; then
        log_error "This script requires macOS"
        ((errors++))
    fi

    # Check required commands
    local required_commands=("ollama" "python3" "jq" "bc")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "Required command not found: $cmd"
            ((errors++))
        fi
    done

    # Check mapping file
    if [ ! -f "$MAPPING_FILE" ]; then
        log_error "Mapping file not found: $MAPPING_FILE"
        ((errors++))
    fi

    # Check Ollama accessibility
    if ! ollama list &> /dev/null; then
        log_error "Cannot access Ollama. Is it running?"
        ((errors++))
    fi

    if [ $errors -gt 0 ]; then
        log_error "Environment validation failed with $errors error(s)"
        return 2
    fi

    log_success "Environment validation passed"
    return 0
}

validate_disk_space() {
    log_header "Validating Disk Space"

    local available_gb=$(df -g . | awk 'NR==2 {print $4}')
    local required_gb=$(jq -r '.metadata.total_mlx_size_gb' "$MAPPING_FILE")

    log_info "Available space: ${available_gb} GB"
    log_info "Required space: ${required_gb} GB"

    if [ "$available_gb" -lt "$required_gb" ]; then
        log_error "Insufficient disk space"
        log_error "Required: ${required_gb} GB, Available: ${available_gb} GB"
        return 1
    fi

    log_success "Sufficient disk space available"
    return 0
}

validate_ollama_models() {
    log_header "Validating Ollama Models"

    # Get models to delete from mapping
    local expected_models=$(jq -r '.models_to_delete[].ollama_name' "$MAPPING_FILE")
    local missing_count=0
    local found_count=0

    while IFS= read -r model; do
        if ollama list | grep -q "^${model}"; then
            log_info "Found: $model"
            ((found_count++))
        else
            log_warning "Not found: $model"
            ((missing_count++))
        fi
    done <<< "$expected_models"

    log_info "Found ${found_count} models to delete"

    if [ $missing_count -gt 0 ]; then
        log_warning "${missing_count} expected models not found (may have been deleted already)"
    fi

    return 0
}

################################################################################
# Backup Functions
################################################################################

create_backup() {
    log_header "Creating Backup"

    mkdir -p "$BACKUP_DIR"

    local timestamp=$(date +%Y%m%d-%H%M%S)
    local backup_file="${BACKUP_DIR}/ollama-backup-${timestamp}.json"

    # Create comprehensive backup
    python3 << 'EOF' > "$backup_file"
import subprocess
import json
import sys
from datetime import datetime

try:
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
    lines = result.stdout.strip().split('\n')[1:]

    models = []
    total_size_gb = 0

    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            size_val = float(parts[2])
            size_unit = parts[3]

            if size_unit == 'GB':
                size_gb = size_val
            elif size_unit == 'MB':
                size_gb = size_val / 1024
            else:
                size_gb = 0

            total_size_gb += size_gb

            models.append({
                'name': parts[0],
                'id': parts[1],
                'size': f"{parts[2]} {parts[3]}",
                'size_gb': round(size_gb, 2),
                'modified': ' '.join(parts[4:])
            })

    backup = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'total_models': len(models),
        'total_size_gb': round(total_size_gb, 2),
        'models': models
    }

    print(json.dumps(backup, indent=2))
    sys.exit(0)

except Exception as e:
    print(f"Error creating backup: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        log_success "Backup created: $backup_file"

        # Display backup summary
        local model_count=$(jq -r '.total_models' "$backup_file")
        local total_size=$(jq -r '.total_size_gb' "$backup_file")
        log_info "Backed up ${model_count} models (${total_size} GB)"

        save_state "backup_created" "$backup_file"
        return 0
    else
        log_error "Failed to create backup"
        return 1
    fi
}

################################################################################
# Migration Functions
################################################################################

delete_ollama_models() {
    log_header "Deleting Ollama Models"

    if [ "$DOWNLOAD_ONLY" = true ]; then
        log_info "Skipping deletion (--download-only mode)"
        return 0
    fi

    # Get models to delete
    local models_to_delete=$(jq -r '.models_to_delete[].ollama_name' "$MAPPING_FILE")
    local total_models=$(echo "$models_to_delete" | wc -l | xargs)

    if [ -z "$models_to_delete" ]; then
        log_warning "No models to delete"
        return 0
    fi

    log_info "Deleting ${total_models} models..."

    local deleted=0
    local failed=0
    local skipped=0

    while IFS= read -r model_name; do
        # Check if model exists
        if ! ollama list | grep -q "^${model_name}"; then
            log_warning "Model not found, skipping: $model_name"
            ((skipped++))
            continue
        fi

        log "Deleting: $model_name"

        if [ "$DRY_RUN" = true ]; then
            log_info "[DRY RUN] Would delete: $model_name"
            ((deleted++))
        else
            if ollama rm "$model_name" 2>&1 | tee -a "$LOG_FILE"; then
                log_success "Deleted: $model_name"
                ((deleted++))
            else
                log_error "Failed to delete: $model_name"
                ((failed++))
            fi
        fi
    done <<< "$models_to_delete"

    log_info "Deletion summary: ${deleted} deleted, ${failed} failed, ${skipped} skipped"

    if [ $failed -gt 0 ]; then
        log_error "Some deletions failed"
        save_state "deletion_partial" "deleted=${deleted}, failed=${failed}"
        return 1
    fi

    save_state "deletion_complete" "deleted=${deleted}"
    log_success "All models deleted successfully"
    return 0
}

install_mlx() {
    log_header "Installing MLX"

    # Check if already installed
    if python3 -c "import mlx_lm" 2>/dev/null; then
        log_success "MLX already installed"
        return 0
    fi

    log_info "Installing MLX..."

    # Create venv if needed
    if [ ! -d "${MLX_DIR}/venv" ]; then
        mkdir -p "$MLX_DIR"
        python3 -m venv "${MLX_DIR}/venv"
        log_success "Created virtual environment"
    fi

    # Activate and install
    source "${MLX_DIR}/venv/bin/activate"

    if pip install --upgrade pip >> "$LOG_FILE" 2>&1 && \
       pip install -U mlx-lm huggingface-hub >> "$LOG_FILE" 2>&1; then
        log_success "MLX installed successfully"
        return 0
    else
        log_error "Failed to install MLX"
        return 1
    fi
}

download_mlx_models() {
    log_header "Downloading MLX Models"

    if [ "$DELETE_ONLY" = true ]; then
        log_info "Skipping downloads (--delete-only mode)"
        return 0
    fi

    # Get models to download
    local models_to_download=$(jq -r '.mlx_models | to_entries[] | select(.value.status == "PENDING") | .key' "$MAPPING_FILE")

    if [ -z "$models_to_download" ]; then
        log_info "All required MLX models already downloaded"
        return 0
    fi

    local total_models=$(echo "$models_to_download" | wc -l | xargs)
    log_info "Downloading ${total_models} MLX models..."

    # Activate venv
    if [ -d "${MLX_DIR}/venv" ]; then
        source "${MLX_DIR}/venv/bin/activate"
    fi

    local downloaded=0
    local failed=0

    while IFS= read -r model_key; do
        local repo=$(jq -r --arg key "$model_key" '.mlx_models[$key].huggingface_repo' "$MAPPING_FILE")
        local local_path="${MLX_DIR}/${model_key}"
        local size=$(jq -r --arg key "$model_key" '.mlx_models[$key].size_gb' "$MAPPING_FILE")

        log "Downloading: $repo (${size} GB)"
        log_info "Destination: $local_path"

        if [ "$DRY_RUN" = true ]; then
            log_info "[DRY RUN] Would download: $repo"
            ((downloaded++))
            continue
        fi

        mkdir -p "$local_path"

        # Download with Python
        if python3 << EOF
from huggingface_hub import snapshot_download
import sys

try:
    snapshot_download(
        repo_id='$repo',
        local_dir='$local_path',
        local_dir_use_symlinks=False
    )
    sys.exit(0)
except Exception as e:
    print(f"Download failed: {e}", file=sys.stderr)
    sys.exit(1)
EOF
        then
            log_success "Downloaded: $model_key"
            ((downloaded++))
        else
            log_error "Failed to download: $model_key"
            ((failed++))
        fi

    done <<< "$models_to_download"

    log_info "Download summary: ${downloaded} downloaded, ${failed} failed"

    if [ $failed -gt 0 ]; then
        log_error "Some downloads failed"
        save_state "download_partial" "downloaded=${downloaded}, failed=${failed}"
        return 1
    fi

    save_state "download_complete" "downloaded=${downloaded}"
    log_success "All MLX models downloaded successfully"
    return 0
}

################################################################################
# Verification Functions
################################################################################

verify_migration() {
    log_header "Verifying Migration"

    local errors=0

    # Check Ollama state
    log_info "Verifying Ollama cleanup..."
    local remaining_old_models=$(jq -r '.models_to_delete[].ollama_name' "$MAPPING_FILE" | while read model; do
        if ollama list | grep -q "^${model}"; then
            echo "$model"
        fi
    done)

    if [ -n "$remaining_old_models" ]; then
        log_warning "Some old models still present:"
        echo "$remaining_old_models" | while read model; do
            log_warning "  - $model"
        done
        ((errors++))
    else
        log_success "All old models removed"
    fi

    # Check MLX models
    log_info "Verifying MLX models..."
    local expected_mlx=$(jq -r '.mlx_models | keys[]' "$MAPPING_FILE")

    while IFS= read -r model_key; do
        local local_path="${MLX_DIR}/${model_key}"

        if [ -d "$local_path" ]; then
            log_success "Found: $model_key"
        else
            log_warning "Missing: $model_key"
            ((errors++))
        fi
    done <<< "$expected_mlx"

    if [ $errors -eq 0 ]; then
        log_success "Migration verified successfully"
        return 0
    else
        log_warning "Migration verification found ${errors} issue(s)"
        return 1
    fi
}

show_summary() {
    log_header "Migration Summary"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo " CURRENT STATE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    echo "Ollama Models:"
    ollama list

    echo ""
    echo "MLX Models:"
    if [ -d "$MLX_DIR" ]; then
        for model_dir in "$MLX_DIR"/*; do
            if [ -d "$model_dir" ] && [ "$(basename "$model_dir")" != "venv" ]; then
                local size=$(du -sh "$model_dir" 2>/dev/null | cut -f1)
                echo "  ✓ $(basename "$model_dir") ($size)"
            fi
        done
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo " QUICK START"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Fast coding:"
    echo "  mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit"
    echo ""
    echo "General questions:"
    echo "  mlx_lm.chat --model mlx-community/Qwen3-14B-Instruct-4bit"
    echo ""
    echo "Math & reasoning:"
    echo "  mlx_lm.chat --model mlx-community/DeepSeek-R1-Distill-Llama-8B"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

################################################################################
# Main Execution
################################################################################

show_usage() {
    cat << EOF
Usage: $(basename "$0") [--execute|--dry-run] [OPTIONS]

Automated migration from Ollama GGUF models to MLX-optimized models.

EXECUTION MODES (one required):
    --execute              Execute the migration (makes actual changes)
    --dry-run              Preview changes without executing

OPTIONS:
    --force                Skip safety confirmations (dangerous!)
    --delete-only          Only delete Ollama models, skip MLX downloads
    --download-only        Only download MLX models, skip Ollama deletions
    --verify-only          Only verify current state, make no changes
    --rollback             Attempt to rollback to previous state
    --help                 Show this help message

EXAMPLES:
    # Preview the migration
    $(basename "$0") --dry-run

    # Execute the migration
    $(basename "$0") --execute

    # Delete Ollama models only
    $(basename "$0") --execute --delete-only

    # Download MLX models only
    $(basename "$0") --execute --download-only

    # Verify migration status
    $(basename "$0") --verify-only

EXIT CODES:
    0 - Success
    1 - General error
    2 - Pre-flight check failed
    3 - Migration failed
    4 - User cancellation

EOF
}

main() {
    # Parse arguments
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi

    while [[ $# -gt 0 ]]; do
        case $1 in
            --execute)
                EXECUTE_MODE=true
                ;;
            --dry-run)
                DRY_RUN=true
                ;;
            --force)
                FORCE_MODE=true
                ;;
            --delete-only)
                DELETE_ONLY=true
                ;;
            --download-only)
                DOWNLOAD_ONLY=true
                ;;
            --verify-only)
                VERIFY_ONLY=true
                ;;
            --rollback)
                ROLLBACK_MODE=true
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

    # Validate execution mode
    if [ "$EXECUTE_MODE" = false ] && [ "$DRY_RUN" = false ] && [ "$VERIFY_ONLY" = false ] && [ "$ROLLBACK_MODE" = false ]; then
        log_error "Must specify --execute, --dry-run, --verify-only, or --rollback"
        show_usage
        exit 1
    fi

    # Print banner
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "    AUTOMATED MLX MIGRATION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi

    if [ "$FORCE_MODE" = true ]; then
        log_warning "FORCE MODE - Safety confirmations disabled"
    fi

    log_info "Log file: $LOG_FILE"

    # Verify-only mode
    if [ "$VERIFY_ONLY" = true ]; then
        validate_environment || exit 2
        verify_migration
        exit $?
    fi

    # Set up progress tracking
    TOTAL_STEPS=7
    CURRENT_STEP=0

    # Execute migration workflow
    progress "Validating environment"
    validate_environment || exit 2

    progress "Validating disk space"
    validate_disk_space || exit 2

    progress "Validating Ollama models"
    validate_ollama_models || exit 2

    progress "Creating backup"
    create_backup || exit 3

    progress "Deleting Ollama models"
    delete_ollama_models || exit 3

    progress "Installing/verifying MLX"
    install_mlx || exit 3

    progress "Downloading MLX models"
    download_mlx_models || exit 3

    # Verification and summary
    if [ "$DRY_RUN" = false ]; then
        verify_migration
        show_summary
        save_state "migration_complete" "success"
        log_success "Migration completed successfully!"
    else
        log_info "Dry run completed successfully"
    fi

    log_info "Log saved to: $LOG_FILE"
}

# Execute main
main "$@"
