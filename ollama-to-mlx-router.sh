#!/bin/bash

################################################################################
# Ollama-to-MLX Router
################################################################################
#
# Intelligent routing script that checks if Ollama is running and falls back
# to MLX if unavailable. Provides convenient command-line access to both
# systems with automatic failover.
#
# Features:
#   - Auto-detect Ollama availability
#   - Seamless fallback to MLX bridge
#   - Support for Ollama CLI commands
#   - Convenient aliases for quick switching
#   - Health monitoring and status reporting
#
# Usage:
#   ./ollama-to-mlx-router.sh run <model> <prompt>
#   ./ollama-to-mlx-router.sh list
#   ./ollama-to-mlx-router.sh status
#   ./ollama-to-mlx-router.sh chat <model>
#
# Examples:
#   ./ollama-to-mlx-router.sh run qwen2.5-coder "Write hello world"
#   ./ollama-to-mlx-router.sh list
#   ./ollama-to-mlx-router.sh status
#
################################################################################

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly RESET='\033[0m'

# Configuration
readonly OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
readonly MLX_BRIDGE_HOST="${MLX_BRIDGE_HOST:-http://localhost:11435}"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly MLX_BRIDGE_SCRIPT="${SCRIPT_DIR}/mlx-ollama-bridge.py"
readonly MLX_VENV="${HOME}/workspace/venv-mlx"

# Timeout for health checks (seconds)
readonly TIMEOUT=5

################################################################################
# Utility Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${RESET} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${RESET} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${RESET} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${RESET} $*" >&2
}

print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Ollama-to-MLX Router v1.0"
    echo "  Intelligent routing with automatic fallback"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${RESET}"
}

################################################################################
# Health Check Functions
################################################################################

check_ollama_health() {
    # Check if Ollama is running and accessible
    if command -v ollama &> /dev/null; then
        if timeout "${TIMEOUT}" curl -s "${OLLAMA_HOST}/api/version" &> /dev/null; then
            return 0
        fi
    fi
    return 1
}

check_mlx_bridge_health() {
    # Check if MLX bridge is running
    if timeout "${TIMEOUT}" curl -s "${MLX_BRIDGE_HOST}/health" &> /dev/null; then
        return 0
    fi
    return 1
}

get_ollama_version() {
    if check_ollama_health; then
        curl -s "${OLLAMA_HOST}/api/version" | grep -o '"version":"[^"]*"' | cut -d'"' -f4
    else
        echo "N/A"
    fi
}

get_mlx_bridge_version() {
    if check_mlx_bridge_health; then
        curl -s "${MLX_BRIDGE_HOST}/api/version" | grep -o '"version":"[^"]*"' | cut -d'"' -f4
    else
        echo "N/A"
    fi
}

################################################################################
# Routing Functions
################################################################################

determine_backend() {
    # Determine which backend to use based on availability
    local backend=""

    if check_ollama_health; then
        backend="ollama"
    elif check_mlx_bridge_health; then
        backend="mlx"
    else
        # Try to start MLX bridge
        log_warning "Neither Ollama nor MLX bridge is running"
        log_info "Attempting to start MLX bridge..."
        start_mlx_bridge_background
        sleep 3

        if check_mlx_bridge_health; then
            backend="mlx"
        else
            log_error "Failed to start MLX bridge"
            return 1
        fi
    fi

    echo "${backend}"
}

get_backend_url() {
    local backend="$1"
    if [[ "${backend}" == "ollama" ]]; then
        echo "${OLLAMA_HOST}"
    else
        echo "${MLX_BRIDGE_HOST}"
    fi
}

################################################################################
# MLX Bridge Management
################################################################################

start_mlx_bridge_background() {
    if [[ ! -f "${MLX_BRIDGE_SCRIPT}" ]]; then
        log_error "MLX bridge script not found: ${MLX_BRIDGE_SCRIPT}"
        return 1
    fi

    if [[ ! -d "${MLX_VENV}" ]]; then
        log_error "MLX virtual environment not found: ${MLX_VENV}"
        log_info "Please create it with: python3 -m venv ${MLX_VENV}"
        log_info "Then install dependencies: pip install flask mlx-lm"
        return 1
    fi

    log_info "Starting MLX bridge on port 11435..."

    # Start in background
    (
        source "${MLX_VENV}/bin/activate"
        python3 "${MLX_BRIDGE_SCRIPT}" --port 11435 &> /tmp/mlx-bridge.log &
        echo $! > /tmp/mlx-bridge.pid
    )

    log_success "MLX bridge started (PID: $(cat /tmp/mlx-bridge.pid 2>/dev/null || echo 'unknown'))"
    log_info "Logs: /tmp/mlx-bridge.log"
}

stop_mlx_bridge() {
    if [[ -f /tmp/mlx-bridge.pid ]]; then
        local pid
        pid=$(cat /tmp/mlx-bridge.pid)
        if kill -0 "${pid}" 2>/dev/null; then
            log_info "Stopping MLX bridge (PID: ${pid})..."
            kill "${pid}"
            rm -f /tmp/mlx-bridge.pid
            log_success "MLX bridge stopped"
        else
            log_warning "MLX bridge process not found"
            rm -f /tmp/mlx-bridge.pid
        fi
    else
        log_warning "MLX bridge PID file not found"
    fi
}

################################################################################
# Command Functions
################################################################################

cmd_status() {
    print_banner

    echo -e "${BOLD}System Status${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Check Ollama
    echo -n "Ollama:            "
    if check_ollama_health; then
        local version
        version=$(get_ollama_version)
        echo -e "${GREEN}Online${RESET} (${OLLAMA_HOST}) - v${version}"
    else
        echo -e "${RED}Offline${RESET} (${OLLAMA_HOST})"
    fi

    # Check MLX Bridge
    echo -n "MLX Bridge:        "
    if check_mlx_bridge_health; then
        local version
        version=$(get_mlx_bridge_version)
        echo -e "${GREEN}Online${RESET} (${MLX_BRIDGE_HOST}) - v${version}"
    else
        echo -e "${RED}Offline${RESET} (${MLX_BRIDGE_HOST})"
    fi

    # Determine active backend
    echo ""
    echo -n "Active Backend:    "
    local backend
    backend=$(determine_backend 2>/dev/null) || true
    if [[ -n "${backend}" ]]; then
        echo -e "${GREEN}${backend}${RESET}"
    else
        echo -e "${RED}None available${RESET}"
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

cmd_list() {
    local backend
    backend=$(determine_backend) || {
        log_error "No backend available"
        exit 1
    }

    local url
    url=$(get_backend_url "${backend}")

    log_info "Listing models from ${backend}..."
    echo ""

    # Fetch and display models
    local response
    response=$(curl -s "${url}/api/tags")

    if command -v jq &> /dev/null; then
        # Pretty print with jq
        echo "${response}" | jq -r '.models[] | "\(.name)\t\(.size / 1073741824 | floor)GB"' | column -t
    else
        # Fallback without jq
        echo "${response}"
    fi
}

cmd_run() {
    local model="$1"
    local prompt="$2"

    local backend
    backend=$(determine_backend) || {
        log_error "No backend available"
        exit 1
    }

    local url
    url=$(get_backend_url "${backend}")

    log_info "Running model '${model}' on ${backend}..."
    echo ""

    # Make API request
    local payload
    payload=$(cat <<EOF
{
    "model": "${model}",
    "prompt": "${prompt}",
    "stream": false
}
EOF
)

    local response
    response=$(curl -s -X POST "${url}/api/generate" \
        -H "Content-Type: application/json" \
        -d "${payload}")

    # Extract and display response
    if command -v jq &> /dev/null; then
        echo -e "${CYAN}Response:${RESET}"
        echo "${response}" | jq -r '.response'
    else
        echo "${response}"
    fi
}

cmd_chat() {
    local model="$1"

    local backend
    backend=$(determine_backend) || {
        log_error "No backend available"
        exit 1
    }

    log_info "Starting interactive chat with '${model}' on ${backend}..."
    log_info "Type 'exit' or 'quit' to end the session"
    echo ""

    local url
    url=$(get_backend_url "${backend}")

    while true; do
        echo -n -e "${GREEN}You: ${RESET}"
        read -r user_input

        if [[ "${user_input}" == "exit" ]] || [[ "${user_input}" == "quit" ]]; then
            log_info "Ending chat session"
            break
        fi

        # Make API request
        local payload
        payload=$(cat <<EOF
{
    "model": "${model}",
    "messages": [
        {"role": "user", "content": "${user_input}"}
    ],
    "stream": false
}
EOF
)

        local response
        response=$(curl -s -X POST "${url}/api/chat" \
            -H "Content-Type: application/json" \
            -d "${payload}")

        # Extract and display response
        echo -n -e "${CYAN}Assistant: ${RESET}"
        if command -v jq &> /dev/null; then
            echo "${response}" | jq -r '.message.content'
        else
            echo "${response}"
        fi
        echo ""
    done
}

cmd_start_mlx() {
    start_mlx_bridge_background
}

cmd_stop_mlx() {
    stop_mlx_bridge
}

cmd_switch() {
    local target="$1"

    case "${target}" in
        ollama)
            log_info "Switching to Ollama..."
            if check_ollama_health; then
                log_success "Ollama is available at ${OLLAMA_HOST}"
                export OLLAMA_HOST
            else
                log_error "Ollama is not running"
                exit 1
            fi
            ;;
        mlx)
            log_info "Switching to MLX..."
            if check_mlx_bridge_health; then
                log_success "MLX bridge is available at ${MLX_BRIDGE_HOST}"
            else
                log_info "Starting MLX bridge..."
                start_mlx_bridge_background
                sleep 3
                if check_mlx_bridge_health; then
                    log_success "MLX bridge started at ${MLX_BRIDGE_HOST}"
                else
                    log_error "Failed to start MLX bridge"
                    exit 1
                fi
            fi
            ;;
        *)
            log_error "Unknown target: ${target}"
            log_info "Use 'ollama' or 'mlx'"
            exit 1
            ;;
    esac
}

################################################################################
# Help Function
################################################################################

show_help() {
    cat <<EOF
${BOLD}Ollama-to-MLX Router${RESET}

Intelligent routing script that checks if Ollama is running and falls back
to MLX if unavailable.

${BOLD}USAGE:${RESET}
    $(basename "$0") <command> [arguments]

${BOLD}COMMANDS:${RESET}
    status                  Show system status (Ollama and MLX bridge)
    list                    List all available models
    run <model> <prompt>    Run a model with a prompt
    chat <model>            Start interactive chat session
    start-mlx               Start MLX bridge in background
    stop-mlx                Stop MLX bridge
    switch <ollama|mlx>     Switch to specific backend
    help                    Show this help message

${BOLD}EXAMPLES:${RESET}
    # Check status
    $(basename "$0") status

    # List models
    $(basename "$0") list

    # Run a model
    $(basename "$0") run qwen2.5-coder "Write a Python hello world"

    # Start chat
    $(basename "$0") chat qwen2.5-coder

    # Start MLX bridge manually
    $(basename "$0") start-mlx

    # Switch to specific backend
    $(basename "$0") switch mlx

${BOLD}ENVIRONMENT VARIABLES:${RESET}
    OLLAMA_HOST            Ollama server URL (default: http://localhost:11434)
    MLX_BRIDGE_HOST        MLX bridge URL (default: http://localhost:11435)

${BOLD}ALIASES:${RESET}
    Add these to your ~/.zshrc or ~/.bashrc for quick access:

    alias ollama-status='$(basename "$0") status'
    alias ollama-list='$(basename "$0") list'
    alias ollama-chat='$(basename "$0") chat'
    alias mlx-start='$(basename "$0") start-mlx'
    alias mlx-stop='$(basename "$0") stop-mlx'

EOF
}

################################################################################
# Main Entry Point
################################################################################

main() {
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi

    local command="$1"
    shift

    case "${command}" in
        status)
            cmd_status
            ;;
        list)
            cmd_list
            ;;
        run)
            if [[ $# -lt 2 ]]; then
                log_error "Usage: run <model> <prompt>"
                exit 1
            fi
            cmd_run "$1" "$2"
            ;;
        chat)
            if [[ $# -lt 1 ]]; then
                log_error "Usage: chat <model>"
                exit 1
            fi
            cmd_chat "$1"
            ;;
        start-mlx)
            cmd_start_mlx
            ;;
        stop-mlx)
            cmd_stop_mlx
            ;;
        switch)
            if [[ $# -lt 1 ]]; then
                log_error "Usage: switch <ollama|mlx>"
                exit 1
            fi
            cmd_switch "$1"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: ${command}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
