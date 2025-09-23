# INGRES AI Chatbot Full Evaluation Script
# This script starts the backend server and runs the evaluation

Write-Host "INGRES AI Chatbot Full Evaluation" -ForegroundColor Green
Write-Host "====================================="

# Check if backend is already running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "Backend server is already running" -ForegroundColor Green
    $backendRunning = $true
} catch {
    Write-Host "🔧 Backend server not running, starting it..." -ForegroundColor Yellow
    $backendRunning = $false
}

if (-not $backendRunning) {
    # Start the backend server in a separate process
    Write-Host "Starting backend server on http://localhost:8000..." -ForegroundColor Yellow
    $serverJob = Start-Job -ScriptBlock {
        Set-Location "C:\Users\mohit\ai-chatbot-ingres\backend"
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
    }
    
    # Wait for server to start
    Write-Host "Waiting for server to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Check if server is now running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 10
        Write-Host "✅ Backend server started successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to start backend server. Running with mock responses..." -ForegroundColor Red
    }
}

# Run the evaluation
Write-Host "`n🔍 Running chatbot evaluation..." -ForegroundColor Cyan
Set-Location "C:\Users\mohit\ai-chatbot-ingres\backend\tests"

try {
    python simple_evaluation.py
    Write-Host "`n✅ Evaluation completed successfully!" -ForegroundColor Green
    Write-Host "📊 Check the evaluation_results folder for detailed reports" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Evaluation failed: $_" -ForegroundColor Red
}

# Stop the server if we started it
if (-not $backendRunning -and $serverJob) {
    Write-Host "`n🛑 Stopping backend server..." -ForegroundColor Yellow
    Stop-Job $serverJob
    Remove-Job $serverJob
    Write-Host "✅ Backend server stopped" -ForegroundColor Green
}

Write-Host "`n🎉 Evaluation process complete!" -ForegroundColor Green
Read-Host "Press Enter to exit"