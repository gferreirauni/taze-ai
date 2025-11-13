# Script de Setup do Taze AI
# Execute este script para configurar o ambiente de desenvolvimento

Write-Host "🚀 Iniciando setup do Taze AI..." -ForegroundColor Cyan
Write-Host ""

# Verificar se Node.js está instalado
Write-Host "📦 Verificando Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js não encontrado. Por favor, instale Node.js 18+ antes de continuar." -ForegroundColor Red
    exit 1
}

# Verificar se Python está instalado
Write-Host "🐍 Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado. Por favor, instale Python 3.10+ antes de continuar." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📚 Instalando dependências do Frontend..." -ForegroundColor Yellow
Set-Location frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao instalar dependências do frontend" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Write-Host "✅ Dependências do frontend instaladas!" -ForegroundColor Green
Set-Location ..

Write-Host ""
Write-Host "🐍 Instalando dependências do Backend..." -ForegroundColor Yellow
Set-Location backend

# Ativar ambiente virtual
& .\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao instalar dependências do backend" -ForegroundColor Red
    deactivate
    Set-Location ..
    exit 1
}
Write-Host "✅ Dependências do backend instaladas!" -ForegroundColor Green

# Desativar ambiente virtual
deactivate
Set-Location ..

Write-Host ""
Write-Host "✨ Setup concluído com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Para rodar o projeto:" -ForegroundColor Cyan
Write-Host "  1. Backend: cd backend && .\venv\Scripts\Activate.ps1 && python main.py" -ForegroundColor White
Write-Host "  2. Frontend (em outro terminal): cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Ou use os scripts na raiz do projeto:" -ForegroundColor Cyan
Write-Host "  - .\start-backend.ps1 (Terminal 1)" -ForegroundColor White
Write-Host "  - .\start-frontend.ps1 (Terminal 2)" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Bom desenvolvimento!" -ForegroundColor Magenta

