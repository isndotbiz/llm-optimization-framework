# Universal Model Runner - Uses llama.cpp in WSL with Ollama fallback
param(
    [Parameter(Mandatory=$false)]
    [string]$ModelName,
    
    [Parameter(Mandatory=$false)]
    [string]$Prompt = "Hello! Who are you?",
    
    [Parameter(Mandatory=$false)]
    [switch]$ListModels,
    
    [Parameter(Mandatory=$false)]
    [switch]$Interactive,
    
    [Parameter(Mandatory=$false)]
    [int]$ContextSize = 4096,
    
    [Parameter(Mandatory=$false)]
    [int]$MaxTokens = 512,
    
    [Parameter(Mandatory=$false)]
    [float]$Temperature = 0.7,
    
    [Parameter(Mandatory=$false)]
    [switch]$UseOllama
)

$ModelRegistry = "D:\models\model-registry.json"

# Load model registry
if (-not (Test-Path $ModelRegistry)) {
    Write-Host "❌ Model registry not found. Run organize-models.ps1 first!" -ForegroundColor Red
    exit 1
}

$registry = Get-Content $ModelRegistry | ConvertFrom-Json

# List models
if ($ListModels) {
    Write-Host "`n📚 Available Models:" -ForegroundColor Cyan
    Write-Host "=" * 80
    foreach ($model in $registry.models) {
        Write-Host "[$($model.index)] $($model.name)" -ForegroundColor Yellow
        Write-Host "    Size: $($model.size_gb) GB" -ForegroundColor Gray
        Write-Host "    File: $($model.file)" -ForegroundColor Gray
    }
    Write-Host "=" * 80
    Write-Host "`nUsage: .\run-model.ps1 -ModelName <name> -Prompt 'Your prompt here'" -ForegroundColor Cyan
    Write-Host "   Or: .\run-model.ps1 -ModelName <name> -Interactive" -ForegroundColor Cyan
    exit 0
}

# Validate model selection
if (-not $ModelName) {
    Write-Host "❌ Please specify a model name or use -ListModels" -ForegroundColor Red
    exit 1
}

# Find model
$selectedModel = $registry.models | Where-Object { 
    $_.name -like "*$ModelName*" -or $_.index -eq $ModelName 
} | Select-Object -First 1

if (-not $selectedModel) {
    Write-Host "❌ Model not found: $ModelName" -ForegroundColor Red
    Write-Host "Use -ListModels to see available models" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n🤖 Using model: $($selectedModel.name) ($($selectedModel.size_gb) GB)" -ForegroundColor Green

# Check if we should use Ollama or llama.cpp
if ($UseOllama) {
    Write-Host "🔄 Using Ollama (Windows)..." -ForegroundColor Cyan
    
    # Check if Ollama is running
    try {
        $ollamaTest = ollama list 2>&1
        Write-Host "✓ Ollama is available" -ForegroundColor Green
    } catch {
        Write-Host "❌ Ollama not found or not running" -ForegroundColor Red
        Write-Host "Install Ollama from: https://ollama.ai" -ForegroundColor Yellow
        exit 1
    }
    
    # For Ollama, we'd need to import the model first
    # This is a simplified version - actual implementation would need model file import
    Write-Host "Note: Direct GGUF usage with Ollama requires model file format" -ForegroundColor Yellow
    Write-Host "Consider using: ollama run <model-name>" -ForegroundColor Yellow
    
} else {
    Write-Host "🐧 Using llama.cpp (WSL)..." -ForegroundColor Cyan
    
    # Check if WSL is available
    try {
        $wslTest = wsl --list --quiet 2>&1
        Write-Host "✓ WSL is available" -ForegroundColor Green
    } catch {
        Write-Host "❌ WSL not found" -ForegroundColor Red
        Write-Host "Falling back to Ollama..." -ForegroundColor Yellow
        $UseOllama = $true
    }
    
    if (-not $UseOllama) {
        # Check if llama.cpp is installed in WSL (CMake build location)
        $llamaCppCheck = wsl bash -c "test -f ~/llama.cpp/build/bin/llama-cli && echo 'found' || echo 'not_found'"

        if ($llamaCppCheck -like "*not_found*") {
            Write-Host "⚠️  llama.cpp not found in WSL" -ForegroundColor Yellow
            Write-Host "Installing llama.cpp..." -ForegroundColor Cyan

            # Install llama.cpp in WSL using CMake
            $installScript = @"
#!/bin/bash
set -e
cd ~
if [ ! -d "llama.cpp" ]; then
    echo "Cloning llama.cpp..."
    git clone https://github.com/ggerganov/llama.cpp.git
fi
cd llama.cpp
git pull
echo "Building llama.cpp with CMake..."
cmake -B build
cmake --build build --config Release -j`$(nproc)
echo "✓ llama.cpp installed successfully"
"@

            $installScript | wsl bash
            $llamaCppPath = "~/llama.cpp/build/bin/llama-cli"
        } else {
            $llamaCppPath = "~/llama.cpp/build/bin/llama-cli"
            Write-Host "✓ Found llama.cpp at: $llamaCppPath" -ForegroundColor Green
        }
        
        # Convert Windows path to WSL path
        $modelPathWSL = $selectedModel.path_wsl
        
        Write-Host "`n🚀 Running model..." -ForegroundColor Cyan
        Write-Host "Model: $modelPathWSL" -ForegroundColor Gray
        Write-Host "Context: $ContextSize | Max Tokens: $MaxTokens | Temp: $Temperature" -ForegroundColor Gray
        Write-Host ("-" * 80) -ForegroundColor Gray
        
        if ($Interactive) {
            # Interactive mode
            wsl bash -c "$llamaCppPath -m '$modelPathWSL' -c $ContextSize -n $MaxTokens --temp $Temperature -i --color"
        } else {
            # Single prompt mode
            $escapedPrompt = $Prompt -replace "'", "'\\''"
            wsl bash -c "$llamaCppPath -m '$modelPathWSL' -c $ContextSize -n $MaxTokens --temp $Temperature -p '$escapedPrompt'"
        }
    }
}
