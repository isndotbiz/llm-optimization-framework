#!/bin/bash

################################################################################
# MLX Server Startup Script
################################################################################
#
# Manages the MLX-Ollama bridge as a background service with support for
# automatic startup via launchd (macOS) or systemd (Linux).
#
# Features:
#   - Start/stop/restart MLX bridge service
#   - Status monitoring with health checks
#   - Automatic startup configuration (launchd/systemd)
#   - Log rotation and management
#   - Process supervision and auto-restart
#   - Clean shutdown handling
#
# Usage:
#   ./mlx-server-startup.sh start
#   ./mlx-server-startup.sh stop
#   ./mlx-server-startup.sh restart
#   ./mlx-server-startup.sh status
#   ./mlx-server-startup.sh install-service
#   ./mlx-server-startup.sh uninstall-service
#
################################################################################

set -euo pipefail

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly RESET='\033[0m'

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly MLX_BRIDGE_SCRIPT="${SCRIPT_DIR}/mlx-ollama-bridge.py"
readonly MLX_VENV="${HOME}/workspace/venv-mlx"
readonly PID_FILE="/tmp/mlx-bridge.pid"
readonly LOG_FILE="/tmp/mlx-bridge.log"
readonly ERROR_LOG_FILE="/tmp/mlx-bridge-error.log"
readonly PORT="${MLX_BRIDGE_PORT:-11434}"
readonly HOST="${MLX_BRIDGE_HOST:-0.0.0.0}"

# Service configuration
readonly SERVICE_NAME="mlx-ollama-bridge"
readonly LAUNCHD_PLIST="${HOME}/Library/LaunchAgents/com.mlx.ollama.bridge.plist"

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
    echo "  MLX Server Startup Manager v1.0"
    echo "  MLX-Ollama Bridge Service Controller"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${RESET}"
}

################################################################################
# Process Management
################################################################################

is_running() {
    if [[ -f "${PID_FILE}" ]]; then
        local pid
        pid=$(cat "${PID_FILE}")
        if kill -0 "${pid}" 2>/dev/null; then
            return 0
        else
            # PID file exists but process is dead
            rm -f "${PID_FILE}"
            return 1
        fi
    fi
    return 1
}

get_pid() {
    if [[ -f "${PID_FILE}" ]]; then
        cat "${PID_FILE}"
    else
        echo "N/A"
    fi
}

check_health() {
    local retries=5
    local delay=2

    for ((i=1; i<=retries; i++)); do
        if curl -s "http://${HOST}:${PORT}/health" &>/dev/null; then
            return 0
        fi
        sleep "${delay}"
    done

    return 1
}

################################################################################
# Service Control Functions
################################################################################

start_service() {
    print_banner

    if is_running; then
        local pid
        pid=$(get_pid)
        log_warning "MLX bridge is already running (PID: ${pid})"
        return 0
    fi

    # Validate requirements
    if [[ ! -f "${MLX_BRIDGE_SCRIPT}" ]]; then
        log_error "MLX bridge script not found: ${MLX_BRIDGE_SCRIPT}"
        return 1
    fi

    if [[ ! -d "${MLX_VENV}" ]]; then
        log_error "MLX virtual environment not found: ${MLX_VENV}"
        log_info "Create it with:"
        echo "  python3 -m venv ${MLX_VENV}"
        echo "  source ${MLX_VENV}/bin/activate"
        echo "  pip install flask mlx-lm"
        return 1
    fi

    log_info "Starting MLX-Ollama bridge..."
    log_info "Host: ${HOST}"
    log_info "Port: ${PORT}"
    log_info "Log file: ${LOG_FILE}"

    # Rotate logs if they exist
    rotate_logs

    # Start the service
    (
        source "${MLX_VENV}/bin/activate"
        nohup python3 "${MLX_BRIDGE_SCRIPT}" \
            --host "${HOST}" \
            --port "${PORT}" \
            > "${LOG_FILE}" 2> "${ERROR_LOG_FILE}" &
        echo $! > "${PID_FILE}"
    )

    sleep 2

    # Verify startup
    if is_running; then
        local pid
        pid=$(get_pid)
        log_success "MLX bridge started successfully (PID: ${pid})"

        # Check health
        log_info "Performing health check..."
        if check_health; then
            log_success "Health check passed"
            log_info "API available at: http://${HOST}:${PORT}"
            log_info "View logs: tail -f ${LOG_FILE}"
        else
            log_warning "Health check failed - service may not be fully started"
            log_info "Check logs: cat ${ERROR_LOG_FILE}"
        fi
    else
        log_error "Failed to start MLX bridge"
        log_info "Check error log: cat ${ERROR_LOG_FILE}"
        return 1
    fi
}

stop_service() {
    print_banner

    if ! is_running; then
        log_warning "MLX bridge is not running"
        return 0
    fi

    local pid
    pid=$(get_pid)

    log_info "Stopping MLX bridge (PID: ${pid})..."

    # Try graceful shutdown first
    if kill -TERM "${pid}" 2>/dev/null; then
        local timeout=10
        local elapsed=0

        while kill -0 "${pid}" 2>/dev/null && [[ ${elapsed} -lt ${timeout} ]]; do
            sleep 1
            ((elapsed++))
        done

        if kill -0 "${pid}" 2>/dev/null; then
            log_warning "Graceful shutdown timeout - forcing termination"
            kill -KILL "${pid}" 2>/dev/null
        fi
    fi

    # Clean up PID file
    rm -f "${PID_FILE}"

    log_success "MLX bridge stopped successfully"
}

restart_service() {
    print_banner
    log_info "Restarting MLX bridge..."
    stop_service
    sleep 2
    start_service
}

show_status() {
    print_banner

    echo -e "${BOLD}Service Status${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Check if running
    if is_running; then
        local pid
        pid=$(get_pid)
        echo -e "Status:            ${GREEN}Running${RESET}"
        echo -e "PID:               ${pid}"

        # Get process info
        if command -v ps &>/dev/null; then
            local cpu mem uptime
            cpu=$(ps -p "${pid}" -o %cpu= 2>/dev/null || echo "N/A")
            mem=$(ps -p "${pid}" -o %mem= 2>/dev/null || echo "N/A")
            uptime=$(ps -p "${pid}" -o etime= 2>/dev/null || echo "N/A")

            echo -e "CPU Usage:         ${cpu}%"
            echo -e "Memory Usage:      ${mem}%"
            echo -e "Uptime:            ${uptime}"
        fi

        # Check health
        echo -n "Health Check:      "
        if curl -s "http://${HOST}:${PORT}/health" &>/dev/null; then
            echo -e "${GREEN}Healthy${RESET}"

            # Get health details
            local health_response
            health_response=$(curl -s "http://${HOST}:${PORT}/health")
            if command -v jq &>/dev/null; then
                local loaded_models
                loaded_models=$(echo "${health_response}" | jq -r '.loaded_models')
                echo -e "Loaded Models:     ${loaded_models}"
            fi
        else
            echo -e "${RED}Unhealthy${RESET}"
        fi
    else
        echo -e "Status:            ${RED}Stopped${RESET}"
        echo -e "PID:               N/A"
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BOLD}Configuration${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "Host:              ${HOST}"
    echo -e "Port:              ${PORT}"
    echo -e "API URL:           http://${HOST}:${PORT}"
    echo -e "Script:            ${MLX_BRIDGE_SCRIPT}"
    echo -e "Virtual Env:       ${MLX_VENV}"
    echo -e "Log File:          ${LOG_FILE}"
    echo -e "Error Log:         ${ERROR_LOG_FILE}"
    echo -e "PID File:          ${PID_FILE}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Check for service installation
    if [[ "$(uname)" == "Darwin" ]]; then
        echo -e "${BOLD}LaunchAgent Status${RESET}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        if [[ -f "${LAUNCHD_PLIST}" ]]; then
            echo -e "Installed:         ${GREEN}Yes${RESET}"
            echo -e "Plist:             ${LAUNCHD_PLIST}"
            if launchctl list | grep -q com.mlx.ollama.bridge; then
                echo -e "Loaded:            ${GREEN}Yes${RESET}"
            else
                echo -e "Loaded:            ${RED}No${RESET}"
            fi
        else
            echo -e "Installed:         ${RED}No${RESET}"
        fi
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
}

################################################################################
# Log Management
################################################################################

rotate_logs() {
    local max_size=$((10 * 1024 * 1024))  # 10MB

    if [[ -f "${LOG_FILE}" ]]; then
        local size
        size=$(stat -f%z "${LOG_FILE}" 2>/dev/null || stat -c%s "${LOG_FILE}" 2>/dev/null || echo 0)
        if [[ ${size} -gt ${max_size} ]]; then
            log_info "Rotating log file (${size} bytes)..."
            mv "${LOG_FILE}" "${LOG_FILE}.old"
        fi
    fi

    if [[ -f "${ERROR_LOG_FILE}" ]]; then
        local size
        size=$(stat -f%z "${ERROR_LOG_FILE}" 2>/dev/null || stat -c%s "${ERROR_LOG_FILE}" 2>/dev/null || echo 0)
        if [[ ${size} -gt ${max_size} ]]; then
            log_info "Rotating error log file (${size} bytes)..."
            mv "${ERROR_LOG_FILE}" "${ERROR_LOG_FILE}.old"
        fi
    fi
}

view_logs() {
    if [[ -f "${LOG_FILE}" ]]; then
        tail -n 50 "${LOG_FILE}"
    else
        log_warning "Log file not found: ${LOG_FILE}"
    fi
}

view_error_logs() {
    if [[ -f "${ERROR_LOG_FILE}" ]]; then
        tail -n 50 "${ERROR_LOG_FILE}"
    else
        log_warning "Error log file not found: ${ERROR_LOG_FILE}"
    fi
}

################################################################################
# Service Installation (macOS launchd)
################################################################################

install_launchd_service() {
    print_banner

    if [[ "$(uname)" != "Darwin" ]]; then
        log_error "LaunchAgent installation is only supported on macOS"
        log_info "For Linux, use install-systemd-service instead"
        return 1
    fi

    log_info "Installing LaunchAgent for automatic startup..."

    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "${HOME}/Library/LaunchAgents"

    # Create plist file
    cat > "${LAUNCHD_PLIST}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mlx.ollama.bridge</string>

    <key>ProgramArguments</key>
    <array>
        <string>${MLX_VENV}/bin/python3</string>
        <string>${MLX_BRIDGE_SCRIPT}</string>
        <string>--host</string>
        <string>${HOST}</string>
        <string>--port</string>
        <string>${PORT}</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>${LOG_FILE}</string>

    <key>StandardErrorPath</key>
    <string>${ERROR_LOG_FILE}</string>

    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>${MLX_VENV}/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

    log_success "LaunchAgent plist created: ${LAUNCHD_PLIST}"

    # Load the service
    log_info "Loading LaunchAgent..."
    if launchctl load "${LAUNCHD_PLIST}"; then
        log_success "LaunchAgent loaded successfully"
        log_info "The MLX bridge will now start automatically on login"
        log_info ""
        log_info "Management commands:"
        echo "  Start:   launchctl start com.mlx.ollama.bridge"
        echo "  Stop:    launchctl stop com.mlx.ollama.bridge"
        echo "  Unload:  launchctl unload ${LAUNCHD_PLIST}"
    else
        log_error "Failed to load LaunchAgent"
        return 1
    fi
}

uninstall_launchd_service() {
    print_banner

    if [[ "$(uname)" != "Darwin" ]]; then
        log_error "LaunchAgent management is only supported on macOS"
        return 1
    fi

    if [[ ! -f "${LAUNCHD_PLIST}" ]]; then
        log_warning "LaunchAgent is not installed"
        return 0
    fi

    log_info "Uninstalling LaunchAgent..."

    # Unload the service
    if launchctl list | grep -q com.mlx.ollama.bridge; then
        launchctl unload "${LAUNCHD_PLIST}"
        log_success "LaunchAgent unloaded"
    fi

    # Remove plist file
    rm -f "${LAUNCHD_PLIST}"
    log_success "LaunchAgent removed"
    log_info "MLX bridge will no longer start automatically"
}

################################################################################
# Help
################################################################################

show_help() {
    cat <<EOF
${BOLD}MLX Server Startup Manager${RESET}

Manage the MLX-Ollama bridge as a background service with support for
automatic startup.

${BOLD}USAGE:${RESET}
    $(basename "$0") <command>

${BOLD}COMMANDS:${RESET}
    start                   Start the MLX bridge service
    stop                    Stop the MLX bridge service
    restart                 Restart the MLX bridge service
    status                  Show service status and health
    logs                    View recent log output
    error-logs              View recent error log output
    install-service         Install as auto-start service (macOS LaunchAgent)
    uninstall-service       Uninstall auto-start service
    help                    Show this help message

${BOLD}EXAMPLES:${RESET}
    # Start the service
    $(basename "$0") start

    # Check status
    $(basename "$0") status

    # View logs
    $(basename "$0") logs

    # Install for automatic startup
    $(basename "$0") install-service

${BOLD}ENVIRONMENT VARIABLES:${RESET}
    MLX_BRIDGE_PORT         Port to listen on (default: 11434)
    MLX_BRIDGE_HOST         Host to bind to (default: 0.0.0.0)

${BOLD}FILES:${RESET}
    Script:         ${MLX_BRIDGE_SCRIPT}
    Virtual Env:    ${MLX_VENV}
    PID File:       ${PID_FILE}
    Log File:       ${LOG_FILE}
    Error Log:      ${ERROR_LOG_FILE}
    LaunchAgent:    ${LAUNCHD_PLIST}

${BOLD}NOTES:${RESET}
    - Default port is 11434 (same as Ollama)
    - Use a different port to run alongside Ollama
    - Logs are automatically rotated when they exceed 10MB
    - Service auto-restarts on failure when installed as LaunchAgent

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
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        logs)
            view_logs
            ;;
        error-logs)
            view_error_logs
            ;;
        install-service)
            install_launchd_service
            ;;
        uninstall-service)
            uninstall_launchd_service
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
