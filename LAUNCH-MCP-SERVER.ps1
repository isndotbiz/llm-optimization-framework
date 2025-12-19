# MCP Server Launcher
# Starts the Model Context Protocol server for PDF and web search tools

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MCP Server Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$MCPDir = "D:\models\mcp_tools"
$MCPScript = "$MCPDir\mcp_server.py"

# Check if script exists
if (-not (Test-Path $MCPScript)) {
    Write-Host "ERROR: mcp_server.py not found!" -ForegroundColor Red
    Write-Host "Expected location: $MCPScript" -ForegroundColor Yellow
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
Write-Host "Checking dependencies..." -ForegroundColor Yellow

# Check if requirements are installed
$requirementsFile = "$MCPDir\requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
    & $pythonCmd -m pip install -q -r $requirementsFile
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Dependencies OK" -ForegroundColor Green
    } else {
        Write-Host "Warning: Some dependencies may not have installed correctly" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Starting MCP Server..." -ForegroundColor Cyan
Write-Host "Server will run in stdio mode (JSON-RPC over stdin/stdout)" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Launch the server
Set-Location $MCPDir
& $pythonCmd $MCPScript

# Keep window open if there was an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Server exited with error code: $LASTEXITCODE" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
