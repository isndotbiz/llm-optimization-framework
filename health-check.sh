#!/bin/bash
# MLX System Health Check
# Quick verification of MLX deployment status

echo "============================================================"
echo "MLX System Health Check"
echo "============================================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
PASSED=0
FAILED=0

# 1. Check virtual environment
echo -n "1. Virtual environment exists... "
if [ -d "$HOME/venv-mlx" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (~/venv-mlx not found)"
    ((FAILED++))
fi

# 2. Check MLX installation
echo -n "2. MLX module installed... "
source ~/venv-mlx/bin/activate 2>/dev/null
if python3 -c "import mlx.core as mx" 2>/dev/null; then
    VERSION=$(python3 -c "import mlx.core as mx; print(mx.__version__)" 2>/dev/null)
    echo -e "${GREEN}✓ PASS${NC} (v$VERSION)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (cannot import mlx)"
    ((FAILED++))
fi

# 3. Check Metal GPU
echo -n "3. Metal GPU available... "
if python3 -c "import mlx.core as mx; assert mx.metal.is_available()" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (Metal GPU not detected)"
    ((FAILED++))
fi

# 4. Check MLX models
echo -n "4. MLX models exist... "
MODEL_COUNT=$(ls mlx/*/config.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$MODEL_COUNT" -eq 6 ]; then
    echo -e "${GREEN}✓ PASS${NC} (6 models found)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARN${NC} ($MODEL_COUNT models found, expected 6)"
    ((FAILED++))
fi

# 5. Check model storage
echo -n "5. Model storage size... "
TOTAL_SIZE=$(du -sh mlx/ 2>/dev/null | awk '{print $1}')
if [ -n "$TOTAL_SIZE" ]; then
    echo -e "${GREEN}✓ PASS${NC} ($TOTAL_SIZE)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (cannot determine size)"
    ((FAILED++))
fi

# 6. Check server script
echo -n "6. MLX server script exists... "
if [ -f "mlx-server.py" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (mlx-server.py not found)"
    ((FAILED++))
fi

# 7. Check port availability
echo -n "7. Port 11434 status... "
if lsof -i :11434 >/dev/null 2>&1; then
    PROCESS=$(lsof -i :11434 | grep -v COMMAND | awk '{print $1}' | head -1)
    echo -e "${YELLOW}⚠ BUSY${NC} ($PROCESS running)"
else
    echo -e "${GREEN}✓ AVAILABLE${NC}"
    ((PASSED++))
fi

# 8. Check benchmark script
echo -n "8. Benchmark script exists... "
if [ -f "benchmark_mlx.py" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARN${NC} (benchmark_mlx.py not found)"
fi

# 9. Check documentation
echo -n "9. Documentation exists... "
if [ -f "FINAL-MLX-DEPLOYMENT.md" ] && [ -f "START-HERE.md" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARN${NC} (docs incomplete)"
fi

# Summary
echo ""
echo "============================================================"
echo "Summary"
echo "============================================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ System is HEALTHY${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. source ~/venv-mlx/bin/activate"
    echo "  2. python3 mlx-server.py"
    echo "  3. curl http://localhost:11434/api/tags | jq"
    exit 0
else
    echo -e "${RED}✗ System has issues${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  - Run: source ~/venv-mlx/bin/activate"
    echo "  - Check: python3 -c 'import mlx.core as mx; print(mx.metal.is_available())'"
    echo "  - Verify: ls mlx/*/config.json"
    echo "  - Read: FINAL-MLX-DEPLOYMENT.md"
    exit 1
fi
