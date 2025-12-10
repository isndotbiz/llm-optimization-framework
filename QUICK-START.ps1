# Quick Start Menu - One-click access to all features

function Show-Menu {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "   AI Router Enhanced - Quick Start" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Choose an option:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1. Launch AI Router Enhanced" -ForegroundColor Green
    Write-Host "  2. Start MCP Server" -ForegroundColor Green
    Write-Host "  3. Run Setup/Install Dependencies" -ForegroundColor Green
    Write-Host "  4. View Documentation" -ForegroundColor Green
    Write-Host "  5. Test MCP Server" -ForegroundColor Green
    Write-Host "  6. Run Original AI Router (Legacy)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  0. Exit" -ForegroundColor Red
    Write-Host ""
}

function Show-Documentation-Menu {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "   Documentation Viewer" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Available documentation:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1. AI Router Enhanced Quick Start" -ForegroundColor White
    Write-Host "  2. Enhanced Features Summary" -ForegroundColor White
    Write-Host "  3. Router Comparison Chart" -ForegroundColor White
    Write-Host "  4. MCP Tools Quick Start" -ForegroundColor White
    Write-Host "  5. Provider Integration Guide" -ForegroundColor White
    Write-Host "  6. System Prompts Reference" -ForegroundColor White
    Write-Host "  7. Main README" -ForegroundColor White
    Write-Host ""
    Write-Host "  0. Back to main menu" -ForegroundColor Red
    Write-Host ""

    $choice = Read-Host "Select documentation to view"

    $docs = @{
        "1" = "D:\models\AI-ROUTER-ENHANCED-QUICKSTART.md"
        "2" = "D:\models\ENHANCED-FEATURES-SUMMARY.md"
        "3" = "D:\models\ROUTER-COMPARISON-CHART.md"
        "4" = "D:\models\mcp_tools\QUICK_START.md"
        "5" = "D:\models\providers\QUICKSTART.md"
        "6" = "D:\models\SYSTEM-PROMPTS-QUICK-REFERENCE.md"
        "7" = "D:\models\README.md"
    }

    if ($docs.ContainsKey($choice)) {
        $docPath = $docs[$choice]
        if (Test-Path $docPath) {
            # Open with default markdown viewer or notepad
            Start-Process $docPath
        } else {
            Write-Host "File not found: $docPath" -ForegroundColor Red
            Read-Host "Press Enter to continue"
        }
    }
}

# Main loop
while ($true) {
    Show-Menu
    $choice = Read-Host "Enter your choice"

    switch ($choice) {
        "1" {
            & "D:\models\LAUNCH-AI-ROUTER-ENHANCED.ps1"
        }
        "2" {
            & "D:\models\LAUNCH-MCP-SERVER.ps1"
        }
        "3" {
            & "D:\models\SETUP-ENVIRONMENT.ps1"
        }
        "4" {
            Show-Documentation-Menu
        }
        "5" {
            Write-Host ""
            Write-Host "Testing MCP Server..." -ForegroundColor Yellow
            python "D:\models\mcp_tools\test_mcp_server.py"
            Read-Host "Press Enter to continue"
        }
        "6" {
            Write-Host ""
            Write-Host "Launching original AI Router..." -ForegroundColor Yellow
            python "D:\models\ai-router.py"
        }
        "0" {
            Write-Host ""
            Write-Host "Goodbye!" -ForegroundColor Cyan
            exit 0
        }
        default {
            Write-Host ""
            Write-Host "Invalid choice. Please try again." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
}
