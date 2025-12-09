# Organize and catalog all GGUF models for llama.cpp and Ollama
# This script finds all models (blobs and .gguf files) and creates symlinks/copies

$ModelsRoot = "D:\models"
$OrganizedDir = "$ModelsRoot\organized"
$ModelRegistry = "$ModelsRoot\model-registry.json"

# Create organized directory
New-Item -ItemType Directory -Force -Path $OrganizedDir | Out-Null

Write-Host "Scanning for models..." -ForegroundColor Cyan

# Find all large files (likely models) - blobs and .gguf files
$allModels = @()

# Get blob files from Ollama cache
$blobs = Get-ChildItem -Path "$ModelsRoot\gguf\blobs" -File -ErrorAction SilentlyContinue | 
    Where-Object {$_.Length -gt 100MB}

foreach ($blob in $blobs) {
    $sizeGB = [math]::Round($blob.Length/1GB, 2)
    $hash = $blob.Name -replace 'sha256-', ''
    
    $allModels += @{
        Type = "blob"
        OriginalPath = $blob.FullName
        Hash = $hash
        SizeGB = $sizeGB
        Name = "model-$hash-${sizeGB}GB"
    }
}

# Get standalone .gguf files
$ggufFiles = Get-ChildItem -Path $ModelsRoot -Filter "*.gguf" -File -ErrorAction SilentlyContinue

foreach ($gguf in $ggufFiles) {
    $sizeGB = [math]::Round($gguf.Length/1GB, 2)
    
    $allModels += @{
        Type = "gguf"
        OriginalPath = $gguf.FullName
        Name = $gguf.BaseName
        SizeGB = $sizeGB
    }
}

Write-Host "`nFound $($allModels.Count) models:" -ForegroundColor Green

# Create organized structure and registry
$registry = @{
    models = @()
    updated = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
}

$modelIndex = 1
foreach ($model in $allModels | Sort-Object -Property SizeGB -Descending) {
    $modelName = $model.Name
    if ($model.Type -eq "blob") {
        $extension = ".gguf"
        $targetName = "$modelName$extension"
    } else {
        $extension = ".gguf"
        $targetName = "$modelName$extension"
    }
    
    $targetPath = Join-Path $OrganizedDir $targetName
    
    Write-Host "[$modelIndex] $modelName ($($model.SizeGB) GB)" -ForegroundColor Yellow
    Write-Host "    Source: $($model.OriginalPath)" -ForegroundColor Gray
    Write-Host "    Target: $targetPath" -ForegroundColor Gray
    
    # Copy or create hardlink to organized directory
    if (-not (Test-Path $targetPath)) {
        try {
            # Try to create hardlink first (saves space)
            New-Item -ItemType HardLink -Path $targetPath -Target $model.OriginalPath -ErrorAction Stop | Out-Null
            Write-Host "    ✓ Hardlink created" -ForegroundColor Green
        } catch {
            # Fallback to copy if hardlink fails
            Copy-Item -Path $model.OriginalPath -Destination $targetPath -Force
            Write-Host "    ✓ Copied" -ForegroundColor Green
        }
    } else {
        Write-Host "    ✓ Already exists" -ForegroundColor Gray
    }
    
    # Add to registry
    $registry.models += @{
        index = $modelIndex
        name = $modelName
        file = $targetName
        path_windows = $targetPath
        path_wsl = ($targetPath -replace '^([A-Z]):', {'/mnt/' + $_.Groups[1].Value.ToLower()}) -replace '\\', '/'
        size_gb = $model.SizeGB
        type = $model.Type
        original_path = $model.OriginalPath
    }
    
    $modelIndex++
}

# Save registry
$registry | ConvertTo-Json -Depth 10 | Set-Content -Path $ModelRegistry -Encoding UTF8

Write-Host "`n✓ Model registry saved to: $ModelRegistry" -ForegroundColor Green
Write-Host "✓ All models organized in: $OrganizedDir" -ForegroundColor Green
Write-Host "`nTotal models: $($allModels.Count)" -ForegroundColor Cyan
Write-Host "Total size: $([math]::Round(($allModels | Measure-Object -Property SizeGB -Sum).Sum, 2)) GB" -ForegroundColor Cyan
