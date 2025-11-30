#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start both NavDrishti backend and frontend servers
.DESCRIPTION
    Starts both servers in separate background processes
#>

Write-Host "🚀 Starting NavDrishti Full Stack..." -ForegroundColor Cyan
Write-Host ""

# Set working directory
Set-Location $PSScriptRoot

# Configure environment for backend
$env:DATABASE_URL = "sqlite:///./navdrishti.db"
$env:SQLALCHEMY_DATABASE_URL = $env:DATABASE_URL

# Start backend in background
Write-Host "📡 Starting Backend on port 8001..." -ForegroundColor Yellow
$venvPath = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$backendProcess = Start-Process -FilePath $venvPath `
    -ArgumentList "-m", "uvicorn", "Traffic_Backend.main:app", "--host", "0.0.0.0", "--port", "8001" `
    -WorkingDirectory $PSScriptRoot `
    -PassThru `
    -NoNewWindow

Start-Sleep -Seconds 3

# Check backend started
$backendRunning = Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue
if ($backendRunning) {
    Write-Host "✅ Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "❌ Backend failed to start" -ForegroundColor Red
    exit 1
}

# Start frontend in background
Write-Host "🌐 Starting Frontend on port 5000..." -ForegroundColor Yellow
$frontendProcess = Start-Process -FilePath "dotnet" `
    -ArgumentList "run", "--no-build" `
    -WorkingDirectory (Join-Path $PSScriptRoot "Traffic_Frontend") `
    -PassThru `
    -NoNewWindow

Start-Sleep -Seconds 4

# Check frontend started
$frontendRunning = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if ($frontendRunning) {
    Write-Host "✅ Frontend started (PID: $($frontendProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend failed to start" -ForegroundColor Red
    Write-Host "Stopping backend..." -ForegroundColor Yellow
    Stop-Process -Id $backendProcess.Id -Force
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎉 NavDrishti is running!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📡 Backend:  http://localhost:8001 (PID: $($backendProcess.Id))" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8001/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:5000 (PID: $($frontendProcess.Id))" -ForegroundColor White
Write-Host "   Dashboard: http://localhost:5000/Home/Dashboard" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop both servers, run: .\stop_all.ps1" -ForegroundColor Yellow
Write-Host ""

# Save PIDs for later stopping
@{
    Backend = $backendProcess.Id
    Frontend = $frontendProcess.Id
} | ConvertTo-Json | Out-File -FilePath (Join-Path $PSScriptRoot ".pids.json")
