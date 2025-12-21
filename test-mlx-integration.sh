#!/bin/bash

################################################################################
# MLX-Ollama Integration Test Script
################################################################################
#
# Verifies the MLX-Ollama integration is properly installed and configured.
#
# Usage:
#   ./test-mlx-integration.sh
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

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}${BOLD}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MLX-Ollama Integration Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${RESET}"

# Test counters
tests_passed=0
tests_failed=0

################################################################################
# Test Functions
################################################################################

test_file_exists() {
    local file="$1"
    local name="$2"

    echo -n "Checking ${name}... "
    if [[ -f "${file}" ]]; then
        echo -e "${GREEN}✓${RESET}"
        ((tests_passed++))
        return 0
    else
        echo -e "${RED}✗ NOT FOUND${RESET}"
        echo "  Expected: ${file}"
        ((tests_failed++))
        return 1
    fi
}

test_file_executable() {
    local file="$1"
    local name="$2"

    echo -n "Checking ${name} executable... "
    if [[ -x "${file}" ]]; then
        echo -e "${GREEN}✓${RESET}"
        ((tests_passed++))
        return 0
    else
        echo -e "${RED}✗ NOT EXECUTABLE${RESET}"
        echo "  Run: chmod +x ${file}"
        ((tests_failed++))
        return 1
    fi
}

test_python_syntax() {
    local file="$1"
    local name="$2"

    echo -n "Checking ${name} Python syntax... "
    if python3 -m py_compile "${file}" 2>/dev/null; then
        echo -e "${GREEN}✓${RESET}"
        ((tests_passed++))
        return 0
    else
        echo -e "${RED}✗ SYNTAX ERROR${RESET}"
        ((tests_failed++))
        return 1
    fi
}

test_bash_syntax() {
    local file="$1"
    local name="$2"

    echo -n "Checking ${name} Bash syntax... "
    if bash -n "${file}" 2>/dev/null; then
        echo -e "${GREEN}✓${RESET}"
        ((tests_passed++))
        return 0
    else
        echo -e "${RED}✗ SYNTAX ERROR${RESET}"
        ((tests_failed++))
        return 1
    fi
}

test_python_dependencies() {
    echo -n "Checking Python dependencies... "

    local missing=()

    if ! python3 -c "import flask" 2>/dev/null; then
        missing+=("flask")
    fi

    if ! python3 -c "import mlx.core" 2>/dev/null; then
        missing+=("mlx")
    fi

    if ! python3 -c "from mlx_lm import load" 2>/dev/null; then
        missing+=("mlx-lm")
    fi

    if [[ ${#missing[@]} -eq 0 ]]; then
        echo -e "${GREEN}✓${RESET}"
        ((tests_passed++))
        return 0
    else
        echo -e "${RED}✗ MISSING: ${missing[*]}${RESET}"
        echo "  Install with: pip install flask mlx-lm"
        ((tests_failed++))
        return 1
    fi
}

test_directory_exists() {
    local dir="$1"
    local name="$2"

    echo -n "Checking ${name}... "
    if [[ -d "${dir}" ]]; then
        echo -e "${GREEN}✓${RESET}"
        ((tests_passed++))
        return 0
    else
        echo -e "${YELLOW}⚠ NOT FOUND${RESET}"
        echo "  Expected: ${dir}"
        ((tests_passed++))  # Don't fail, just warn
        return 0
    fi
}

################################################################################
# Run Tests
################################################################################

echo -e "${BOLD}File Existence Tests${RESET}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_file_exists \
    "${SCRIPT_DIR}/mlx-ollama-bridge.py" \
    "MLX-Ollama Bridge"

test_file_exists \
    "${SCRIPT_DIR}/ollama-to-mlx-router.sh" \
    "Ollama-to-MLX Router"

test_file_exists \
    "${SCRIPT_DIR}/mlx-server-startup.sh" \
    "MLX Server Startup"

test_file_exists \
    "${SCRIPT_DIR}/MLX-OLLAMA-INTEGRATION-GUIDE.md" \
    "Integration Guide"

test_file_exists \
    "${SCRIPT_DIR}/MLX-OLLAMA-QUICKSTART.md" \
    "Quick Start Guide"

echo ""
echo -e "${BOLD}Executable Permissions${RESET}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_file_executable \
    "${SCRIPT_DIR}/mlx-ollama-bridge.py" \
    "MLX-Ollama Bridge"

test_file_executable \
    "${SCRIPT_DIR}/ollama-to-mlx-router.sh" \
    "Router Script"

test_file_executable \
    "${SCRIPT_DIR}/mlx-server-startup.sh" \
    "Startup Script"

echo ""
echo -e "${BOLD}Syntax Validation${RESET}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_python_syntax \
    "${SCRIPT_DIR}/mlx-ollama-bridge.py" \
    "MLX-Ollama Bridge"

test_bash_syntax \
    "${SCRIPT_DIR}/ollama-to-mlx-router.sh" \
    "Router Script"

test_bash_syntax \
    "${SCRIPT_DIR}/mlx-server-startup.sh" \
    "Startup Script"

echo ""
echo -e "${BOLD}Dependency Checks${RESET}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_python_dependencies

test_directory_exists \
    "${HOME}/workspace/mlx" \
    "MLX Models Directory"

test_directory_exists \
    "${HOME}/workspace/venv-mlx" \
    "MLX Virtual Environment"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BOLD}Test Results${RESET}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

total_tests=$((tests_passed + tests_failed))
pass_rate=$((tests_passed * 100 / total_tests))

echo -e "Total tests:   ${total_tests}"
echo -e "Passed:        ${GREEN}${tests_passed}${RESET}"
echo -e "Failed:        ${RED}${tests_failed}${RESET}"
echo -e "Pass rate:     ${pass_rate}%"

echo ""

if [[ ${tests_failed} -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}✓ All tests passed!${RESET}"
    echo ""
    echo "Next steps:"
    echo "  1. Start the MLX bridge:"
    echo "     ./mlx-server-startup.sh start"
    echo ""
    echo "  2. Check status:"
    echo "     ./ollama-to-mlx-router.sh status"
    echo ""
    echo "  3. Try a chat:"
    echo "     ./ollama-to-mlx-router.sh chat qwen2.5-coder"
    exit 0
else
    echo -e "${RED}${BOLD}✗ Some tests failed${RESET}"
    echo ""
    echo "Please fix the issues above before proceeding."
    echo ""
    echo "Common fixes:"
    echo "  - Install dependencies: pip install flask mlx-lm"
    echo "  - Make scripts executable: chmod +x *.sh *.py"
    echo "  - Setup MLX: See MACBOOK-MLX-SETUP-GUIDE.md"
    exit 1
fi
