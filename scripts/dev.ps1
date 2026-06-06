# Quick dev script for Windows (PowerShell)
# Run from repo root to start both backend (mock) and frontend

Write-Host "Starting ROCmForge dev environment (MOCK mode)..." -ForegroundColor Cyan

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:ROCFORGE_MOCK='1'; cd '$PSScriptRoot\..'; python -m uvicorn src.main:app --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 2

# Start frontend
cd frontend
npm run dev

Write-Host "Frontend will be at http://localhost:3000" -ForegroundColor Green