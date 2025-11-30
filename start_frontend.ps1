#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the NavDrishti frontend server
.DESCRIPTION
    Starts the ASP.NET Core frontend on port 5000
#>

Write-Host "🚀 Starting NavDrishti Frontend..." -ForegroundColor Cyan

# Set working directory
Set-Location (Join-Path $PSScriptRoot "Traffic_Frontend")

# Check if backend is running
try {
    $backendTest = Invoke-WebRequest -Uri "http://localhost:8001/projects/" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    Write-Host "✅ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Backend not detected on port 8001" -ForegroundColor Yellow
    Write-Host "   Start backend first: .\start_backend.ps1" -ForegroundColor Yellow
    Write-Host ""
}

# Start the frontend
Write-Host "🌐 Frontend will be available at http://localhost:5000" -ForegroundColor Green
Write-Host "📊 Dashboard at http://localhost:5000/Home/Dashboard" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

dotnet run --no-build
