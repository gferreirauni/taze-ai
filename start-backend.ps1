# Script para iniciar o Backend do Taze AI

Write-Host "🐍 Iniciando Backend Taze AI..." -ForegroundColor Cyan
Write-Host ""

Set-Location backend

# Ativar ambiente virtual
& .\venv\Scripts\Activate.ps1

Write-Host "✅ Ambiente virtual ativado" -ForegroundColor Green
Write-Host "🚀 Iniciando servidor FastAPI em http://localhost:8000" -ForegroundColor Yellow
Write-Host "📚 Documentação disponível em http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python main.py

