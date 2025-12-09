# Monitor llama.cpp Performance and Alert on Degradation

param(
    [Parameter(Mandatory=$true)]
    [string]$ModelPath,

    [int]$ExpectedMinToksPerSec = 20,

    [int]$TestTokens = 100
)

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  LLAMA.CPP PERFORMANCE MONITOR" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Testing model: $ModelPath" -ForegroundColor Cyan
Write-Host "Expected minimum: $ExpectedMinToksPerSec tok/sec`n" -ForegroundColor Cyan

# Convert Windows path to WSL
$WslPath = $ModelPath -replace 'D:\\', '/mnt/d/' -replace '\\', '/'

# Run performance test
Write-Host "Running performance test ($TestTokens tokens)..." -ForegroundColor Yellow

$testPrompt = "The quick brown fox jumps over the lazy dog. This is a test prompt to measure inference performance."

$output = wsl bash -c "~/llama.cpp/build/bin/llama-cli -m '$WslPath' -p '$testPrompt' -n $TestTokens -t 24 -b 2048 --no-ppl -ngl 99 2>&1"

# Extract performance metrics
$promptEvalTime = $null
$evalTime = $null
$promptToksPerSec = $null
$toksPerSec = $null

foreach ($line in $output -split "`n") {
    if ($line -match "prompt eval time.*?(\d+\.\d+) ms.*?(\d+\.\d+) tokens per second") {
        $promptEvalTime = [double]$Matches[1]
        $promptToksPerSec = [double]$Matches[2]
    }
    if ($line -match "eval time.*?(\d+\.\d+) ms.*?(\d+\.\d+) tokens per second") {
        $evalTime = [double]$Matches[1]
        $toksPerSec = [double]$Matches[2]
    }
}

# Display results
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  PERFORMANCE RESULTS" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

if ($toksPerSec) {
    Write-Host "Prompt Processing: $promptToksPerSec tok/sec ($promptEvalTime ms)" -ForegroundColor White
    Write-Host "Token Generation:  $toksPerSec tok/sec ($evalTime ms)" -ForegroundColor White

    # Check if performance meets expectations
    if ($toksPerSec -lt $ExpectedMinToksPerSec) {
        Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
        Write-Host "║  ⚠️  PERFORMANCE DEGRADATION DETECTED!" -ForegroundColor Red
        Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Red

        Write-Host "Current:  $toksPerSec tok/sec" -ForegroundColor Red
        Write-Host "Expected: >$ExpectedMinToksPerSec tok/sec" -ForegroundColor Yellow
        Write-Host "Deficit:  $([math]::Round($ExpectedMinToksPerSec - $toksPerSec, 2)) tok/sec below target`n" -ForegroundColor Red

        Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
        Write-Host "║  TROUBLESHOOTING STEPS" -ForegroundColor Yellow
        Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Yellow

        # Diagnostic checks
        Write-Host "1. Checking GPU offloading..." -ForegroundColor Cyan
        if ($output -match "-ngl \d+") {
            Write-Host "   ✓ GPU layers parameter found" -ForegroundColor Green
        } else {
            Write-Host "   ✗ Missing -ngl parameter! Add: -ngl 99" -ForegroundColor Red
        }

        Write-Host "`n2. Checking if using WSL..." -ForegroundColor Cyan
        if ($ModelPath -match "wsl" -or $WslPath -match "/mnt/") {
            Write-Host "   ✓ Using WSL path" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  May be using Windows version (45-60% slower)" -ForegroundColor Yellow
        }

        Write-Host "`n3. Checking batch size..." -ForegroundColor Cyan
        if ($output -match "-b (\d+)") {
            $batchSize = [int]$Matches[1]
            if ($batchSize -eq 2048) {
                Write-Host "   ✓ Optimal batch size ($batchSize)" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  Suboptimal batch size ($batchSize). Use: -b 2048" -ForegroundColor Yellow
            }
        }

        Write-Host "`n4. Checking thread count..." -ForegroundColor Cyan
        if ($output -match "-t (\d+)") {
            $threads = [int]$Matches[1]
            if ($threads -eq 24) {
                Write-Host "   ✓ Using all threads ($threads)" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  Not using all threads ($threads/24). Use: -t 24" -ForegroundColor Yellow
            }
        }

        Write-Host "`n5. Checking for background GPU usage..." -ForegroundColor Cyan
        $gpuProc = wsl bash -c "nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader 2>/dev/null"
        if ($gpuProc) {
            Write-Host "   ⚠️  Other processes using GPU:" -ForegroundColor Yellow
            Write-Host "   $gpuProc" -ForegroundColor White
        } else {
            Write-Host "   ✓ No other GPU processes detected" -ForegroundColor Green
        }

        Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
        Write-Host "║  RECOMMENDED ACTIONS" -ForegroundColor Yellow
        Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Yellow

        Write-Host "1. Ensure using WSL llama.cpp, not Windows version" -ForegroundColor White
        Write-Host "2. Verify GPU offloading: -ngl 99" -ForegroundColor White
        Write-Host "3. Use optimal parameters: -t 24 -b 2048 --no-ppl" -ForegroundColor White
        Write-Host "4. Close other GPU-intensive applications" -ForegroundColor White
        Write-Host "5. Run: .\ENSURE-WSL-USAGE.ps1 for full diagnostic" -ForegroundColor White

    } else {
        Write-Host "`n✓ Performance is GOOD ($toksPerSec tok/sec >= $ExpectedMinToksPerSec expected)" -ForegroundColor Green

        # Show performance rating
        $percentAbove = [math]::Round((($toksPerSec / $ExpectedMinToksPerSec) - 1) * 100, 1)

        if ($toksPerSec -gt $ExpectedMinToksPerSec * 1.5) {
            Write-Host "   Rating: EXCELLENT (+$percentAbove% above target)" -ForegroundColor Green
        } elseif ($toksPerSec -gt $ExpectedMinToksPerSec * 1.2) {
            Write-Host "   Rating: VERY GOOD (+$percentAbove% above target)" -ForegroundColor Green
        } else {
            Write-Host "   Rating: GOOD (meeting target)" -ForegroundColor Green
        }
    }

} else {
    Write-Host "✗ Could not extract performance metrics from output" -ForegroundColor Red
    Write-Host "`nRaw output:" -ForegroundColor Yellow
    Write-Host $output
}

Write-Host "`n✓ Performance check complete!`n" -ForegroundColor Green
