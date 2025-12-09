# Enforce WSL usage for llama.cpp (45-60% faster than Windows)
# Run this periodically to ensure no Windows LLM tools are being used

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  WSL LLAMA.CPP ENFORCEMENT CHECK" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check for Windows LLM executables (these are slower!)
$WinExecutables = @(
    @{Path="C:\Program Files\Ollama\ollama.exe"; Name="Ollama"},
    @{Path="C:\ProgramData\chocolatey\bin\llama.exe"; Name="Chocolatey llama"},
    @{Path="$env:LOCALAPPDATA\Programs\llamacpp\llama.exe"; Name="Local llama.cpp"},
    @{Path="C:\Program Files\LM Studio\lms.exe"; Name="LM Studio"}
)

$foundWindows = $false
foreach ($exe in $WinExecutables) {
    if (Test-Path $exe.Path) {
        Write-Host "⚠️  WARNING: Windows LLM tool found: $($exe.Name)" -ForegroundColor Red
        Write-Host "   Location: $($exe.Path)" -ForegroundColor Yellow
        Write-Host "   Impact: 45-60% SLOWER than WSL llama.cpp`n" -ForegroundColor Red
        $foundWindows = $true
    }
}

if ($foundWindows) {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║  RECOMMENDED ACTION" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Yellow
    Write-Host "Remove Windows LLM tools and use WSL exclusively for optimal performance.`n" -ForegroundColor Yellow

    Write-Host "To uninstall:" -ForegroundColor Cyan
    Write-Host "  Ollama:     winget uninstall Ollama.Ollama" -ForegroundColor White
    Write-Host "  LM Studio:  winget uninstall LMStudio" -ForegroundColor White
    Write-Host "`nAlways use: wsl bash -c '~/llama.cpp/build/bin/llama-cli ...'`n" -ForegroundColor Green
} else {
    Write-Host "✓ No Windows LLM executables found (good!)" -ForegroundColor Green
}

# Verify WSL llama.cpp is properly installed
Write-Host "`nChecking WSL llama.cpp installation..." -ForegroundColor Cyan

$wslCheck = wsl bash -c "test -f ~/llama.cpp/build/bin/llama-cli && echo 'OK' || echo 'MISSING'"

if ($wslCheck -eq "OK") {
    Write-Host "✓ WSL llama.cpp is properly installed" -ForegroundColor Green

    # Check if it's compiled with CUDA support
    $cudaCheck = wsl bash -c "~/llama.cpp/build/bin/llama-cli --version 2>&1 | grep -i cuda"

    if ($cudaCheck) {
        Write-Host "✓ CUDA support enabled (GPU acceleration active)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  CUDA support NOT detected" -ForegroundColor Yellow
        Write-Host "   Recompile with: make clean && make LLAMA_CUBLAS=1" -ForegroundColor Yellow
    }

    # Check version
    $version = wsl bash -c "~/llama.cpp/build/bin/llama-cli --version 2>&1 | head -1"
    Write-Host "   Version: $version" -ForegroundColor Cyan

} else {
    Write-Host "✗ WSL llama.cpp NOT found!" -ForegroundColor Red
    Write-Host "`nInstall with:" -ForegroundColor Yellow
    Write-Host "wsl bash -c 'cd ~ && git clone https://github.com/ggerganov/llama.cpp && cd llama.cpp && make LLAMA_CUBLAS=1'" -ForegroundColor White
}

# Check for PowerShell profile aliases (warn about Ollama/Windows usage)
Write-Host "`nChecking PowerShell profile for safety aliases..." -ForegroundColor Cyan

if (Test-Path $PROFILE) {
    $profileContent = Get-Content $PROFILE -Raw

    if ($profileContent -match "function ollama" -and $profileContent -match "function llama") {
        Write-Host "✓ Safety aliases found in PowerShell profile" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Safety aliases NOT found" -ForegroundColor Yellow
        Write-Host "`nAdd these to your PowerShell profile ($PROFILE):`n" -ForegroundColor Yellow

        $aliasCode = @"
# Prevent accidental use of non-optimized LLM tools
function ollama {
    Write-Host "⚠️  Don't use Ollama! Use WSL llama.cpp instead (45-60% faster)" -ForegroundColor Red
    Write-Host "Run: wsl bash -c '~/llama.cpp/build/bin/llama-cli -m /mnt/d/models/...'" -ForegroundColor Yellow
}

function llama {
    Write-Host "⚠️  Use WSL llama.cpp, not Windows version" -ForegroundColor Red
    Write-Host "Run: wsl bash -c '~/llama.cpp/build/bin/llama-cli ...'" -ForegroundColor Yellow
}
"@

        Write-Host $aliasCode -ForegroundColor White
    }
} else {
    Write-Host "⚠️  PowerShell profile not found at: $PROFILE" -ForegroundColor Yellow
    Write-Host "Create it to add safety aliases" -ForegroundColor Yellow
}

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  SUMMARY" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Correct usage:" -ForegroundColor Green
Write-Host "wsl bash -c '~/llama.cpp/build/bin/llama-cli -m /mnt/d/models/organized/[model].gguf -p \`"prompt\`" -ngl 99 -t 24 -b 2048 --no-ppl'" -ForegroundColor White

Write-Host "`nOptimal parameters:" -ForegroundColor Green
Write-Host "  -ngl 99          (GPU offload all layers)" -ForegroundColor White
Write-Host "  -t 24            (Use all CPU threads)" -ForegroundColor White
Write-Host "  -b 2048          (Optimal batch size for 24GB VRAM)" -ForegroundColor White
Write-Host "  --no-ppl         (Skip perplexity, +15% speed)" -ForegroundColor White

Write-Host "`n✓ Enforcement check complete!`n" -ForegroundColor Green
