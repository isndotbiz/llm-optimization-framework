# LAUNCH-AI-ROUTER.ps1
# Launches the AI Router application in WSL for optimal performance
#
# Usage: .\LAUNCH-AI-ROUTER.ps1

param(
    [switch]$InstallDependencies
)

Write-Host "=== AI Router Launcher (WSL) ===" -ForegroundColor Cyan
Write-Host ""

# Check if WSL is available
try {
    $wslCheck = wsl --list --quiet 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: WSL is not available or not installed" -ForegroundColor Red
        Write-Host "Please install WSL first: wsl --install" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "ERROR: WSL is not available" -ForegroundColor Red
    exit 1
}

# Install Python dependencies in WSL if requested
if ($InstallDependencies) {
    Write-Host "Installing Python dependencies in WSL..." -ForegroundColor Yellow
    wsl bash -c "python3 -m pip install --user colorama termcolor rich 2>&1"
    Write-Host "Dependencies installed!" -ForegroundColor Green
    Write-Host ""
}

# Convert Windows path to WSL path
$wslPath = "/mnt/d/models"

Write-Host "Launching AI Router in WSL..." -ForegroundColor Green
Write-Host "Path: $wslPath" -ForegroundColor Gray
Write-Host "Python: WSL Python3 (venv)" -ForegroundColor Gray
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Launch the AI Router in WSL using the hf_venv virtual environment
wsl bash -c "cd '$wslPath' && ~/hf_venv/bin/python3 ai-router.py"

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "AI Router exited with error code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Run with -InstallDependencies flag to install Python packages" -ForegroundColor Gray
    Write-Host "   .\LAUNCH-AI-ROUTER.ps1 -InstallDependencies" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Verify Python3 is installed in WSL:" -ForegroundColor Gray
    Write-Host "   wsl bash -c 'python3 --version'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Verify the file exists:" -ForegroundColor Gray
    Write-Host "   wsl bash -c 'ls -la /mnt/d/models/ai-router.py'" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "AI Router exited successfully" -ForegroundColor Green
}
