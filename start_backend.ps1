#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the NavDrishti backend server
.DESCRIPTION
    Starts the FastAPI backend on port 8001 with SQLite database
#>

Write-Host "🚀 Starting NavDrishti Backend..." -ForegroundColor Cyan

# Set working directory
Set-Location $PSScriptRoot

# Configure environment
$env:DATABASE_URL = "sqlite:///./navdrishti.db"
$env:SQLALCHEMY_DATABASE_URL = $env:DATABASE_URL

# Check if virtual environment exists
$venvPath = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPath)) {
    Write-Host "❌ Virtual environment not found at $venvPath" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Start the backend
Write-Host "📡 Backend will be available at http://localhost:8001" -ForegroundColor Green
Write-Host "📄 API docs at http://localhost:8001/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

& $venvPath -m uvicorn Traffic_Backend.main:app --host 0.0.0.0 --port 8001 --reload
