# Leave Management Agent - Auto Start with Browser
# This script reliably starts the app and opens browser every time

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LEAVE MANAGEMENT AGENT HRMS" -ForegroundColor Green
Write-Host "  Starting Application..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Kill any existing Streamlit processes
Write-Host "Checking for existing Streamlit processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*streamlit*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Start Streamlit in background
Write-Host "Starting Streamlit server..." -ForegroundColor Yellow
$streamlitProcess = Start-Process -FilePath "python" -ArgumentList "-m", "streamlit", "run", "app.py", "--server.headless=true", "--server.port=8501", "--browser.gatherUsageStats=false" -PassThru -WindowStyle Hidden

# Wait for server to be ready
Write-Host "Waiting for server to initialize..." -ForegroundColor Yellow
$maxAttempts = 20
$attempt = 0
$serverReady = $false

while ($attempt -lt $maxAttempts -and !$serverReady) {
    Start-Sleep -Seconds 1
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $serverReady = $true
        }
    }
    catch {
        $attempt++
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
}

Write-Host ""

if ($serverReady) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Server Ready! Opening Browser..." -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # Open browser - Try multiple methods for reliability
    $url = "http://localhost:8501"
    
    # Method 1: Start-Process (most reliable)
    Start-Process $url
    
    # Wait a moment then try Method 2 as backup
    Start-Sleep -Seconds 2
    
    # Method 2: Direct browser executable
    $browsers = @(
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "$env:ProgramFiles (x86)\Google\Chrome\Application\chrome.exe",
        "$env:LocalAppData\Google\Chrome\Application\chrome.exe",
        "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles (x86)\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Mozilla Firefox\firefox.exe",
        "$env:ProgramFiles (x86)\Mozilla Firefox\firefox.exe"
    )
    
    $browserOpened = $false
    foreach ($browser in $browsers) {
        if (Test-Path $browser) {
            if (!$browserOpened) {
                Start-Process $browser -ArgumentList $url -ErrorAction SilentlyContinue
                $browserOpened = $true
            }
            break
        }
    }
    
    Write-Host "✅ Application Started Successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📌 Access URL: http://localhost:8501" -ForegroundColor Cyan
    Write-Host "🔐 Admin Login: admin@example.com / admin123" -ForegroundColor Yellow
    Write-Host "👤 Employee Login: alice@example.com / password123" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "⚠️  Press Ctrl+C to stop the server" -ForegroundColor Red
    Write-Host "❌ Or close this window to stop" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Keep window open and monitor process
    try {
        while ($streamlitProcess -and !$streamlitProcess.HasExited) {
            Start-Sleep -Seconds 5
        }
    }
    catch {
        Write-Host "Server stopped." -ForegroundColor Yellow
    }
}
else {
    Write-Host ""
    Write-Host "❌ Failed to start server. Please check:" -ForegroundColor Red
    Write-Host "   1. Python is installed" -ForegroundColor Yellow
    Write-Host "   2. Streamlit is installed (pip install streamlit)" -ForegroundColor Yellow
    Write-Host "   3. Port 8501 is not in use" -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "Press Enter to exit"
