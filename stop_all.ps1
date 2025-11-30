#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Stop both NavDrishti backend and frontend servers
#>

Write-Host "🛑 Stopping NavDrishti servers..." -ForegroundColor Yellow

# Try to load saved PIDs
$pidsFile = Join-Path $PSScriptRoot ".pids.json"
if (Test-Path $pidsFile) {
    $pids = Get-Content $pidsFile | ConvertFrom-Json
    
    if ($pids.Backend) {
        try {
            Stop-Process -Id $pids.Backend -Force -ErrorAction SilentlyContinue
            Write-Host "✅ Stopped backend (PID: $($pids.Backend))" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Backend process not found" -ForegroundColor Yellow
        }
    }
    
    if ($pids.Frontend) {
        try {
            Stop-Process -Id $pids.Frontend -Force -ErrorAction SilentlyContinue
            Write-Host "✅ Stopped frontend (PID: $($pids.Frontend))" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Frontend process not found" -ForegroundColor Yellow
        }
    }
    
    Remove-Item $pidsFile -ErrorAction SilentlyContinue
}

# Also kill any processes on the ports
Write-Host "🔍 Checking for processes on ports 8001 and 5000..." -ForegroundColor Gray

$port8001 = Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue
if ($port8001) {
    $pid = $port8001[0].OwningProcess
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Killed process on port 8001 (PID: $pid)" -ForegroundColor Green
}

$port5000 = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if ($port5000) {
    $pid = $port5000[0].OwningProcess
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Killed process on port 5000 (PID: $pid)" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ All servers stopped" -ForegroundColor Green
