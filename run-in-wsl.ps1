# Direct WSL Model Runner - Native Linux Performance
# Much faster than PowerShell wrapper - runs directly in WSL

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
    [int]$TopK = 40,

    [Parameter(Mandatory=$false)]
    [float]$TopP = 0.95
)

$ModelRegistry = "D:\models\model-registry.json"

# Load model registry
if (-not (Test-Path $ModelRegistry)) {
    Write-Host "❌ Model registry not found!" -ForegroundColor Red
    exit 1
}

$registry = Get-Content $ModelRegistry | ConvertFrom-Json

# List models function
if ($ListModels) {
    Write-Host "`n📚 RTX 3090 Models (organized folder):" -ForegroundColor Cyan
    foreach ($model in $registry.rtx3090_24gb.models) {
        Write-Host "  [$($model.index)] $($model.name)" -ForegroundColor Yellow
        Write-Host "       $($model.best_for)" -ForegroundColor Gray
    }
    Write-Host "`n📚 RTX 4060 Ti Models (server):" -ForegroundColor Cyan
    foreach ($model in $registry.rtx4060ti_16gb.models) {
        Write-Host "  [$($model.index)] $($model.name)" -ForegroundColor Yellow
        Write-Host "       $($model.best_for)" -ForegroundColor Gray
    }
    Write-Host "`nUsage: .\\run-in-wsl.ps1 -ModelName <name> -Prompt 'Your prompt'" -ForegroundColor Cyan
    exit 0
}

if (-not $ModelName) {
    Write-Host "❌ Specify a model name or use -ListModels" -ForegroundColor Red
    exit 1
}

# Search for model in both GPU setups
$selectedModel = $null
$modelPath = $null

foreach ($model in $registry.rtx3090_24gb.models) {
    if ($model.name -like "*$ModelName*" -or $model.file -like "*$ModelName*") {
        $selectedModel = $model
        $modelPath = "/mnt/d/models/organized/$($model.file)"
        break
    }
}

if (-not $selectedModel) {
    foreach ($model in $registry.rtx4060ti_16gb.models) {
        if ($model.name -like "*$ModelName*" -or $model.file -like "*$ModelName*") {
            $selectedModel = $model
            $modelPath = "/mnt/d/models/rtx4060ti-16gb/$($model.file)"
            if ($model.location) {
                $modelPath = "/mnt/d/models/rtx4060ti-16gb/$($model.location)$($model.file)"
            }
            break
        }
    }
}

if (-not $selectedModel) {
    Write-Host "❌ Model not found: $ModelName" -ForegroundColor Red
    exit 1
}

Write-Host "`n🚀 WSL Native Runner" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "Model: $($selectedModel.name)" -ForegroundColor Cyan
Write-Host "Size: $($selectedModel.size_gb)GB | Quant: $($selectedModel.quantization)" -ForegroundColor Gray
Write-Host "Path: $modelPath" -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "Context: $ContextSize | Max Tokens: $MaxTokens | Temp: $Temperature" -ForegroundColor Gray
Write-Host ""

# Verify file exists
$wslTest = wsl bash -c "test -f '$modelPath' && echo 'found' || echo 'not_found'"
if ($wslTest -like "*not_found*") {
    Write-Host "❌ Model file not found at: $modelPath" -ForegroundColor Red
    exit 1
}

# Build llama.cpp command with optimizations for RTX 3090
# Optimization flags:
#  -t 24 : Use all CPU threads
#  -b 2048 : Batch size for faster processing
#  --no-ppl : Skip perplexity calculation for speed
$threadCount = 24  # WSL CPU count
$batchSize = 2048

$llamaCmd = "~/llama.cpp/build/bin/llama-cli -m '$modelPath' -c $ContextSize -n $MaxTokens --temp $Temperature -k $TopK -p $TopP -t $threadCount -b $batchSize --no-ppl"

if ($Interactive) {
    # Interactive mode
    $llamaCmd += " -i --color"
    wsl bash -c "$llamaCmd"
} else {
    # Single prompt mode - escape special characters
    $escapedPrompt = $Prompt -replace '"', '\"' -replace '`', '``' -replace '$', '`$'
    $llamaCmd += " -p `"$escapedPrompt`""
    wsl bash -c "$llamaCmd"
}

Write-Host ""
Write-Host "✓ Done" -ForegroundColor Green
