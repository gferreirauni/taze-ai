# Script Simples para Iniciar Taze AI
# Sem emojis para compatibilidade com Windows

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   TAZE AI - Inicializacao Automatica      " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Node.js
Write-Host "Verificando Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "OK - Node.js instalado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO - Node.js nao encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "OK - Python instalado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO - Python nao encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   INSTALANDO DEPENDENCIAS DO BACKEND      " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Ir para backend e instalar dependencias
Write-Host "Instalando pacotes Python..." -ForegroundColor Yellow
Set-Location backend

# Ativar venv
& .\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao instalar dependencias!" -ForegroundColor Red
    exit 1
}

Write-Host "OK - Dependencias instaladas!" -ForegroundColor Green

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   VERIFICANDO CONFIGURACAO OPENAI         " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se .env existe
if (Test-Path ".env") {
    Write-Host "OK - Arquivo .env encontrado!" -ForegroundColor Green
    $envContent = Get-Content .env -Raw
    if ($envContent -match "sk-") {
        Write-Host "OK - OpenAI API Key configurada!" -ForegroundColor Green
    } else {
        Write-Host "AVISO - .env existe mas sem chave valida" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Para usar o chat com IA, adicione sua chave OpenAI em backend\.env" -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "AVISO - Arquivo .env nao encontrado!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Criando arquivo .env de exemplo..." -ForegroundColor Cyan
    
    $envTemplate = @"
OPENAI_API_KEY=sk-sua-chave-da-openai-aqui
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
"@
    
    Set-Content -Path ".env" -Value $envTemplate
    Write-Host "OK - Arquivo .env criado em backend\.env" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANTE: Edite o arquivo e adicione sua chave OpenAI!" -ForegroundColor Yellow
    Write-Host "Comando: notepad backend\.env" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "        CONFIGURACAO CONCLUIDA!            " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

Write-Host "Agora execute em 2 terminais separados:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 1 (Backend):" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 (Frontend):" -ForegroundColor Yellow
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Depois abra: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

# Voltar para raiz
Set-Location ..

