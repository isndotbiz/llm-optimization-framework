# AI Router Enhanced Launcher
# Automatically launches the enhanced AI Router with all features

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Router Enhanced v2.0 Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ModelsDir = "D:\models"
$RouterScript = "$ModelsDir\ai-router-enhanced.py"

# Check if script exists
if (-not (Test-Path $RouterScript)) {
    Write-Host "ERROR: ai-router-enhanced.py not found!" -ForegroundColor Red
    Write-Host "Expected location: $RouterScript" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Checking Python installation..." -ForegroundColor Yellow

# Check Python
$pythonCmd = $null
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} else {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

$pythonVersion = & $pythonCmd --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

Write-Host ""
Write-Host "Launching AI Router Enhanced..." -ForegroundColor Cyan
Write-Host ""

# Launch the router
Set-Location $ModelsDir
& $pythonCmd $RouterScript

# Keep window open if there was an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Router exited with error code: $LASTEXITCODE" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
