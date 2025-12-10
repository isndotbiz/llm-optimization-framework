# Complete Environment Setup Script
# Sets up all dependencies and configurations for AI Router Enhanced

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Router Enhanced Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ModelsDir = "D:\models"

# Check Python
Write-Host "Step 1: Checking Python installation..." -ForegroundColor Yellow
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

# Install MCP server dependencies
Write-Host ""
Write-Host "Step 2: Installing MCP Server dependencies..." -ForegroundColor Yellow
$mcpRequirements = "$ModelsDir\mcp_tools\requirements.txt"
if (Test-Path $mcpRequirements) {
    & $pythonCmd -m pip install -r $mcpRequirements
    if ($LASTEXITCODE -eq 0) {
        Write-Host "MCP dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "Warning: Some MCP dependencies may not have installed" -ForegroundColor Yellow
    }
}

# Install provider dependencies
Write-Host ""
Write-Host "Step 3: Installing Provider dependencies..." -ForegroundColor Yellow
$providerRequirements = "$ModelsDir\providers\requirements.txt"
if (Test-Path $providerRequirements) {
    & $pythonCmd -m pip install -r $providerRequirements
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Provider dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "Warning: Some provider dependencies may not have installed" -ForegroundColor Yellow
    }
}

# Create directories if they don't exist
Write-Host ""
Write-Host "Step 4: Creating directory structure..." -ForegroundColor Yellow

$directories = @(
    "$ModelsDir\projects",
    "$ModelsDir\bots",
    "$ModelsDir\mcp_tools",
    "$ModelsDir\providers",
    "$ModelsDir\archive"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "Exists: $dir" -ForegroundColor Gray
    }
}

# Check for llama.cpp in WSL (if on Windows)
Write-Host ""
Write-Host "Step 5: Checking llama.cpp installation..." -ForegroundColor Yellow

if ($IsWindows -or $env:OS -eq "Windows_NT") {
    Write-Host "Detected Windows environment" -ForegroundColor Cyan

    # Check WSL
    if (Get-Command wsl -ErrorAction SilentlyContinue) {
        Write-Host "WSL found - checking llama.cpp..." -ForegroundColor Yellow

        $llamaCheck = wsl bash -c "test -f ~/llama.cpp/build/bin/llama-cli && echo 'found' || echo 'not found'"

        if ($llamaCheck -eq "found") {
            Write-Host "llama.cpp is installed in WSL" -ForegroundColor Green
        } else {
            Write-Host "WARNING: llama.cpp not found in WSL" -ForegroundColor Yellow
            Write-Host "For local model execution, install llama.cpp in WSL:" -ForegroundColor Yellow
            Write-Host "  wsl" -ForegroundColor Gray
            Write-Host "  git clone https://github.com/ggerganov/llama.cpp.git" -ForegroundColor Gray
            Write-Host "  cd llama.cpp" -ForegroundColor Gray
            Write-Host "  make -j" -ForegroundColor Gray
        }
    } else {
        Write-Host "WARNING: WSL not found" -ForegroundColor Yellow
        Write-Host "For optimal local model performance, install WSL 2" -ForegroundColor Yellow
        Write-Host "Run: wsl --install" -ForegroundColor Gray
    }
}

# Check Ollama (optional)
Write-Host ""
Write-Host "Step 6: Checking optional dependencies..." -ForegroundColor Yellow

if (Get-Command ollama -ErrorAction SilentlyContinue) {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "Ollama found: $ollamaVersion" -ForegroundColor Green
} else {
    Write-Host "Ollama not found (optional - for Ollama provider)" -ForegroundColor Gray
    Write-Host "Download from: https://ollama.com" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: .\LAUNCH-AI-ROUTER-ENHANCED.ps1" -ForegroundColor White
Write-Host "2. Create your first project" -ForegroundColor White
Write-Host "3. Configure providers (if using cloud APIs)" -ForegroundColor White
Write-Host ""
Write-Host "Documentation available in:" -ForegroundColor Yellow
Write-Host "  - AI-ROUTER-ENHANCED-QUICKSTART.md" -ForegroundColor White
Write-Host "  - ENHANCED-FEATURES-SUMMARY.md" -ForegroundColor White
Write-Host "  - README.md" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
