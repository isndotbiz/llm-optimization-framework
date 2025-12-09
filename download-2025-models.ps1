# Download Best 2025 Models - Optimized for RTX 3090 (24GB) and RTX 4060 Ti (16GB)
# Based on comprehensive research of HuggingFace, OpenRouter, Reddit, and community recommendations

param(
    [Parameter(Mandatory=$false)]
    [switch]$RTX3090Only,

    [Parameter(Mandatory=$false)]
    [switch]$RTX4060Only,

    [Parameter(Mandatory=$false)]
    [switch]$SkipMove
)

$ErrorActionPreference = "Continue"

Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "  2025 MODEL DOWNLOAD SCRIPT" -ForegroundColor Cyan
Write-Host "  Optimized for RTX 3090 (24GB) and RTX 4060 Ti (16GB)" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Create directory structure
Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
$rtx3090Dir = "D:\models\rtx3090-24gb"
$rtx4060Dir = "D:\models\rtx4060ti-16gb"
$organizedDir = "D:\models\organized"

New-Item -ItemType Directory -Force -Path $rtx3090Dir | Out-Null
New-Item -ItemType Directory -Force -Path $rtx4060Dir | Out-Null
New-Item -ItemType Directory -Force -Path $organizedDir | Out-Null

Write-Host "✓ Directories created" -ForegroundColor Green
Write-Host ""

# Check if HuggingFace CLI is available
Write-Host "🔍 Checking HuggingFace CLI..." -ForegroundColor Yellow
$hfCheck = wsl bash -c "test -f ~/hf_venv/bin/hf && echo 'found' || echo 'not_found'"

if ($hfCheck -like "*not_found*") {
    Write-Host "⚠️  HuggingFace CLI not found. Setting up..." -ForegroundColor Yellow
    wsl bash -c "python3 -m venv ~/hf_venv && ~/hf_venv/bin/pip install -q huggingface_hub"
    Write-Host "✓ HuggingFace CLI installed" -ForegroundColor Green
} else {
    Write-Host "✓ HuggingFace CLI ready" -ForegroundColor Green
}
Write-Host ""

# RTX 3090 Models (24GB VRAM)
$rtx3090Models = @(
    @{
        Name = "Llama 3.3 70B Abliterated (IQ3_XS)"
        Repo = "bartowski/Llama-3.3-70B-Instruct-abliterated-GGUF"
        Pattern = "*IQ3_XS.gguf"
        Dir = "llama-3.3-70b-abliterated"
        Size = "~23GB"
        Description = "BEST UNCENSORED 2025 - 128K context, equivalent to 405B quality"
    },
    @{
        Name = "Dolphin-Mistral-24B-Venice Edition (Q4_K_M)"
        Repo = "bartowski/cognitivecomputations_Dolphin-Mistral-24B-Venice-Edition-GGUF"
        Pattern = "*Q4_K_M.gguf"
        Dir = "dolphin-mistral-24b-venice"
        Size = "~14GB"
        Description = "LOWEST REFUSAL RATE (2.20%) - Purpose-built for 24GB GPUs"
    },
    @{
        Name = "Qwen 2.5 Coder 32B (Q4_K_M)"
        Repo = "bartowski/Qwen2.5-Coder-32B-Instruct-GGUF"
        Pattern = "*Q4_K_M.gguf"
        Dir = "qwen25-coder-32b"
        Size = "~19GB"
        Description = "BEST CODING 2025 - 92 languages, 88.4% HumanEval"
    },
    @{
        Name = "Phi-4 14B (Q6_K)"
        Repo = "bartowski/Phi-4-GGUF"
        Pattern = "*Q6_K.gguf"
        Dir = "phi-4-14b"
        Size = "~11GB"
        Description = "BEST REASONING - Microsoft's new model, beats GPT-4 on benchmarks"
    },
    @{
        Name = "MythoMax-L2-13B (Q6_K)"
        Repo = "bartowski/MythoMax-L2-13B-GGUF"
        Pattern = "*Q6_K.gguf"
        Dir = "mythomax-13b-q6k"
        Size = "~10GB"
        Description = "CREATIVE WRITING - Upgrade from Q5_K_M for better quality"
    }
)

# RTX 4060 Ti Models (16GB VRAM)
$rtx4060Models = @(
    @{
        Name = "Qwen 2.5 14B Instruct (Q4_K_M)"
        Repo = "Qwen/Qwen2.5-14B-Instruct-GGUF"
        Pattern = "*q4_k_m.gguf"
        Dir = "qwen25-14b-instruct"
        Size = "~9GB"
        Description = "PRIMARY DAILY DRIVER - Competitive with GPT-4o-mini"
    },
    @{
        Name = "Qwen 2.5 Coder 7B (Q5_K_M)"
        Repo = "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF"
        Pattern = "*q5_k_m.gguf"
        Dir = "qwen25-coder-7b"
        Size = "~5.4GB"
        Description = "CODING SPECIALIST - 84.8 HumanEval, fast responses"
    },
    @{
        Name = "Llama 3.1 8B Instruct (Q6_K)"
        Repo = "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF"
        Pattern = "*Q6_K.gguf"
        Dir = "llama31-8b-instruct"
        Size = "~6.6GB"
        Description = "RELIABLE GENERAL - Professional writing, summarization"
    },
    @{
        Name = "Qwen 2.5 14B Uncensored (Q4_K_M)"
        Repo = "bartowski/Qwen2.5-14B_Uncensored_Instruct-GGUF"
        Pattern = "*Q4_K_M.gguf"
        Dir = "qwen25-14b-uncensored"
        Size = "~9GB"
        Description = "UNCENSORED ALTERNATIVE - Technical work without restrictions"
    }
)

# Download function
function Start-ModelDownload {
    param(
        [string]$Name,
        [string]$Repo,
        [string]$Pattern,
        [string]$TargetDir,
        [string]$Size,
        [string]$Description
    )

    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "📦 $Name" -ForegroundColor Cyan
    Write-Host "   Size: $Size" -ForegroundColor Gray
    Write-Host "   $Description" -ForegroundColor Gray
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

    $cmd = "~/hf_venv/bin/hf download $Repo --include '$Pattern' --local-dir $TargetDir 2>&1"

    Write-Host "⏳ Downloading..." -ForegroundColor Yellow
    $result = wsl bash -c $cmd

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Downloaded successfully!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "✗ Download failed!" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
        return $false
    }
}

# Download RTX 3090 models
if (-not $RTX4060Only) {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║  RTX 3090 (24GB VRAM) - MODELS                                                 ║" -ForegroundColor Magenta
    Write-Host "║  Total: ~77GB                                                                  ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta

    $rtx3090Success = 0
    $rtx3090Total = $rtx3090Models.Count

    foreach ($model in $rtx3090Models) {
        $targetDir = "/mnt/d/models/rtx3090-24gb/$($model.Dir)"
        $success = Start-ModelDownload -Name $model.Name -Repo $model.Repo -Pattern $model.Pattern -TargetDir $targetDir -Size $model.Size -Description $model.Description
        if ($success) { $rtx3090Success++ }
    }

    Write-Host ""
    Write-Host "RTX 3090 Downloads: $rtx3090Success/$rtx3090Total successful" -ForegroundColor $(if ($rtx3090Success -eq $rtx3090Total) { "Green" } else { "Yellow" })
}

# Download RTX 4060 Ti models
if (-not $RTX3090Only) {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  RTX 4060 Ti (16GB VRAM) - SERVER MODELS                                       ║" -ForegroundColor Cyan
    Write-Host "║  Total: ~30GB                                                                  ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    $rtx4060Success = 0
    $rtx4060Total = $rtx4060Models.Count

    foreach ($model in $rtx4060Models) {
        $targetDir = "/mnt/d/models/rtx4060ti-16gb/$($model.Dir)"
        $success = Start-ModelDownload -Name $model.Name -Repo $model.Repo -Pattern $model.Pattern -TargetDir $targetDir -Size $model.Size -Description $model.Description
        if ($success) { $rtx4060Success++ }
    }

    Write-Host ""
    Write-Host "RTX 4060 Ti Downloads: $rtx4060Success/$rtx4060Total successful" -ForegroundColor $(if ($rtx4060Success -eq $rtx4060Total) { "Green" } else { "Yellow" })
}

# Copy Dolphin 3.0 (already downloaded)
if (-not $RTX3090Only) {
    Write-Host ""
    Write-Host "📋 Copying existing Dolphin 3.0 Llama 3.1 8B to RTX 4060 Ti folder..." -ForegroundColor Yellow
    if (Test-Path "D:\models\organized\Dolphin3.0-Llama3.1-8B-Q6_K.gguf") {
        Copy-Item "D:\models\organized\Dolphin3.0-Llama3.1-8B-Q6_K.gguf" "$rtx4060Dir\Dolphin3.0-Llama3.1-8B-Q6_K.gguf" -Force
        Write-Host "✓ Copied Dolphin 3.0 (already downloaded)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Dolphin 3.0 not found in organized folder" -ForegroundColor Yellow
    }
}

# Move models to organized folder
if (-not $SkipMove) {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "📦 ORGANIZING MODELS" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

    Write-Host ""
    Write-Host "Moving RTX 3090 models to organized folder..." -ForegroundColor Yellow
    Get-ChildItem -Path "$rtx3090Dir\*\*.gguf" -Recurse -File | ForEach-Object {
        Write-Host "  Moving: $($_.Name)" -ForegroundColor Gray
        Move-Item $_.FullName "$organizedDir\" -Force
    }

    Write-Host ""
    Write-Host "✓ RTX 3090 models organized" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Note: RTX 4060 Ti models kept separate in: $rtx4060Dir" -ForegroundColor Cyan
    Write-Host "   Transfer these to your server when ready." -ForegroundColor Cyan

    # Update model registry
    Write-Host ""
    Write-Host "Updating model registry..." -ForegroundColor Yellow
    & "D:\models\organize-models.ps1"
    Write-Host "✓ Model registry updated" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "═" * 80 -ForegroundColor Green
Write-Host "  DOWNLOAD COMPLETE!" -ForegroundColor Green
Write-Host "═" * 80 -ForegroundColor Green
Write-Host ""

if (-not $RTX4060Only) {
    Write-Host "RTX 3090 (24GB) Models:" -ForegroundColor Cyan
    Write-Host "  Location: D:\models\organized\" -ForegroundColor Gray
    Write-Host "  Models:" -ForegroundColor Gray
    Write-Host "    • Llama 3.3 70B Abliterated (IQ3_XS) - Best uncensored 2025" -ForegroundColor Gray
    Write-Host "    • Dolphin-Mistral-24B-Venice (Q4_K_M) - Lowest refusal rate" -ForegroundColor Gray
    Write-Host "    • Qwen 2.5 Coder 32B (Q4_K_M) - Best coding" -ForegroundColor Gray
    Write-Host "    • Phi-4 14B (Q6_K) - Best reasoning" -ForegroundColor Gray
    Write-Host "    • MythoMax-L2-13B (Q6_K) - Creative writing" -ForegroundColor Gray
    Write-Host ""
}

if (-not $RTX3090Only) {
    Write-Host "RTX 4060 Ti (16GB) Models:" -ForegroundColor Cyan
    Write-Host "  Location: D:\models\rtx4060ti-16gb\" -ForegroundColor Gray
    Write-Host "  Models:" -ForegroundColor Gray
    Write-Host "    • Qwen 2.5 14B Instruct (Q4_K_M) - Daily driver" -ForegroundColor Gray
    Write-Host "    • Qwen 2.5 Coder 7B (Q5_K_M) - Coding" -ForegroundColor Gray
    Write-Host "    • Llama 3.1 8B Instruct (Q6_K) - General purpose" -ForegroundColor Gray
    Write-Host "    • Qwen 2.5 14B Uncensored (Q4_K_M) - Uncensored" -ForegroundColor Gray
    Write-Host "    • Dolphin 3.0 Llama 3.1 8B (Q6_K) - Uncensored fast" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test models with: .\run-model.ps1 -ListModels" -ForegroundColor Gray
Write-Host "  2. Run a test: .\run-model.ps1 -ModelName 'llama-3.3' -Prompt 'Hello!'" -ForegroundColor Gray
Write-Host "  3. Transfer RTX 4060 Ti models to your server" -ForegroundColor Gray
Write-Host ""

Write-Host "═" * 80 -ForegroundColor Green
Write-Host ""
