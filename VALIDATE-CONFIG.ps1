# Validate llama.cpp Commands for Optimal Parameters

param(
    [string]$Command = "",
    [string]$ScriptFile = ""
)

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  LLAMA.CPP CONFIGURATION VALIDATOR" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

function Test-LlamaCppCommand {
    param([string]$Cmd)

    $issues = @()
    $warnings = @()
    $info = @()

    # Check GPU offloading
    if ($Cmd -notmatch "-ngl") {
        $issues += "CRITICAL: Missing GPU offloading (-ngl). Add: -ngl 99"
    } elseif ($Cmd -match "-ngl (\d+)") {
        $ngl = [int]$Matches[1]
        if ($ngl -lt 99) {
            $warnings += "Suboptimal GPU offloading (-ngl $ngl). Recommended: -ngl 99"
        } else {
            $info += "✓ GPU offloading optimal (-ngl $ngl)"
        }
    }

    # Check thread count
    if ($Cmd -notmatch "-t") {
        $warnings += "Missing thread specification (-t). Recommended: -t 24"
    } elseif ($Cmd -match "-t (\d+)") {
        $threads = [int]$Matches[1]
        if ($threads -ne 24) {
            $warnings += "Suboptimal thread count (-t $threads). Recommended: -t 24 for Ryzen 9 5900X"
        } else {
            $info += "✓ Thread count optimal (-t 24)"
        }
    }

    # Check batch size
    if ($Cmd -notmatch "-b") {
        $warnings += "Missing batch size (-b). Recommended: -b 2048 for 24GB VRAM"
    } elseif ($Cmd -match "-b (\d+)") {
        $batch = [int]$Matches[1]
        if ($batch -ne 2048) {
            $warnings += "Suboptimal batch size (-b $batch). Recommended: -b 2048 for 24GB VRAM"
        } else {
            $info += "✓ Batch size optimal (-b 2048)"
        }
    }

    # Check --no-ppl flag
    if ($Cmd -notmatch "--no-ppl") {
        $warnings += "Missing --no-ppl flag (free 15% speedup). Add: --no-ppl"
    } else {
        $info += "✓ Using --no-ppl (15% speedup)"
    }

    # Check if using WSL
    if ($Cmd -match "ollama" -or $Cmd -notmatch "wsl") {
        $issues += "CRITICAL: Not using WSL! 45-60% slower than WSL llama.cpp"
    } else {
        $info += "✓ Using WSL (optimal)"
    }

    # Model-specific checks
    if ($Cmd -match "Qwen" -or $Cmd -match "qwen") {
        if ($Cmd -match "--temp 0") {
            $issues += "CRITICAL: Qwen models require temperature >= 0.6, not 0.0 (causes errors)"
        }
        if ($Cmd -notmatch "--jinja") {
            $warnings += "Qwen models recommended: --jinja flag"
        } else {
            $info += "✓ Using --jinja for Qwen model"
        }
    }

    if ($Cmd -match "Phi-4" -or $Cmd -match "phi") {
        if ($Cmd -notmatch "--jinja") {
            $issues += "CRITICAL: Phi-4 requires --jinja flag to enable reasoning format"
        } else {
            $info += "✓ Using --jinja for Phi-4 model"
        }
    }

    if ($Cmd -match "Ministral" -or $Cmd -match "ministral") {
        if ($Cmd -notmatch "-c \d{6,}") {
            $warnings += "Ministral-3 has 256K context - consider using larger -c value"
        }
    }

    # Check temperature range
    if ($Cmd -match "--temp (\d+\.?\d*)") {
        $temp = [double]$Matches[1]
        if ($temp -gt 1.5) {
            $warnings += "Very high temperature ($temp) may produce incoherent output"
        }
    }

    return @{
        Issues = $issues
        Warnings = $warnings
        Info = $info
    }
}

# Main validation logic
if ($Command) {
    # Validate single command
    Write-Host "Validating command:`n$Command`n" -ForegroundColor Cyan

    $validation = Test-LlamaCppCommand -Cmd $Command

    if ($validation.Issues.Count -eq 0 -and $validation.Warnings.Count -eq 0) {
        Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║  ✓ COMMAND IS FULLY OPTIMIZED" -ForegroundColor Green
        Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
    }

    if ($validation.Issues.Count -gt 0) {
        Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
        Write-Host "║  CRITICAL ISSUES" -ForegroundColor Red
        Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Red
        $validation.Issues | ForEach-Object { Write-Host "  ✗ $_" -ForegroundColor Red }
        Write-Host ""
    }

    if ($validation.Warnings.Count -gt 0) {
        Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
        Write-Host "║  WARNINGS" -ForegroundColor Yellow
        Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Yellow
        $validation.Warnings | ForEach-Object { Write-Host "  ⚠  $_" -ForegroundColor Yellow }
        Write-Host ""
    }

    if ($validation.Info.Count -gt 0) {
        Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║  OPTIMIZATIONS FOUND" -ForegroundColor Green
        Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
        $validation.Info | ForEach-Object { Write-Host "  $_" -ForegroundColor Green }
        Write-Host ""
    }

} elseif ($ScriptFile) {
    # Validate all commands in a script file
    if (-not (Test-Path $ScriptFile)) {
        Write-Host "Error: Script file not found: $ScriptFile" -ForegroundColor Red
        exit 1
    }

    Write-Host "Validating all llama.cpp commands in: $ScriptFile`n" -ForegroundColor Cyan

    $content = Get-Content $ScriptFile -Raw
    $commands = [regex]::Matches($content, "llama-cli[^\n]+")

    if ($commands.Count -eq 0) {
        Write-Host "No llama-cli commands found in file" -ForegroundColor Yellow
    } else {
        Write-Host "Found $($commands.Count) command(s)`n" -ForegroundColor Green

        $totalIssues = 0
        $totalWarnings = 0

        for ($i = 0; $i -lt $commands.Count; $i++) {
            Write-Host "Command $($i + 1):" -ForegroundColor Cyan
            Write-Host $commands[$i].Value -ForegroundColor White

            $validation = Test-LlamaCppCommand -Cmd $commands[$i].Value

            if ($validation.Issues.Count -gt 0) {
                Write-Host "Issues:" -ForegroundColor Red
                $validation.Issues | ForEach-Object { Write-Host "  ✗ $_" -ForegroundColor Red }
                $totalIssues += $validation.Issues.Count
            }

            if ($validation.Warnings.Count -gt 0) {
                Write-Host "Warnings:" -ForegroundColor Yellow
                $validation.Warnings | ForEach-Object { Write-Host "  ⚠  $_" -ForegroundColor Yellow }
                $totalWarnings += $validation.Warnings.Count
            }

            Write-Host ""
        }

        Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
        Write-Host "║  SUMMARY" -ForegroundColor Cyan
        Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

        Write-Host "Commands checked: $($commands.Count)" -ForegroundColor White
        Write-Host "Critical issues:  $totalIssues" -ForegroundColor $(if ($totalIssues -gt 0) { "Red" } else { "Green" })
        Write-Host "Warnings:         $totalWarnings" -ForegroundColor $(if ($totalWarnings -gt 0) { "Yellow" } else { "Green" })
    }

} else {
    # No input provided - show usage
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  Validate single command:" -ForegroundColor Cyan
    Write-Host "    .\VALIDATE-CONFIG.ps1 -Command 'wsl bash -c `"llama-cli -m model.gguf ...`"'" -ForegroundColor White
    Write-Host "`n  Validate script file:" -ForegroundColor Cyan
    Write-Host "    .\VALIDATE-CONFIG.ps1 -ScriptFile D:\models\myscript.ps1" -ForegroundColor White

    Write-Host "`nExample of fully optimized command:" -ForegroundColor Yellow
    Write-Host "wsl bash -c `"~/llama.cpp/build/bin/llama-cli -m /mnt/d/models/organized/model.gguf -p 'prompt' -ngl 99 -t 24 -b 2048 --no-ppl`"" -ForegroundColor Green
}

Write-Host "`n✓ Validation complete!`n" -ForegroundColor Green
