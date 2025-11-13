# 🧪 Script de Teste Completo - Taze AI
# Execute este script para testar tudo automaticamente

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        🧪 TAZE AI - TESTE AUTOMÁTICO COMPLETO 🧪            ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar Node.js
Write-Host "📦 Verificando Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js instalado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js não encontrado! Instale antes de continuar." -ForegroundColor Red
    exit 1
}

# Verificar Python
Write-Host "🐍 Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python instalado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado! Instale antes de continuar." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "                    CONFIGURAÇÃO OPENAI                        " -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar se .env existe
$envPath = "backend\.env"
if (Test-Path $envPath) {
    Write-Host "✅ Arquivo .env encontrado!" -ForegroundColor Green
    $envContent = Get-Content $envPath
    if ($envContent -match "sk-") {
        Write-Host "✅ OpenAI API Key configurada!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  .env existe mas sem chave válida" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "🔑 Por favor, adicione sua OpenAI API Key no arquivo backend\.env" -ForegroundColor Yellow
        Write-Host "   Formato: OPENAI_API_KEY=sk-sua-chave-aqui" -ForegroundColor White
        Write-Host ""
        $continue = Read-Host "Deseja continuar mesmo assim? (s/n)"
        if ($continue -ne "s") {
            exit 0
        }
    }
} else {
    Write-Host "⚠️  Arquivo .env NÃO encontrado!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Criando arquivo .env de exemplo..." -ForegroundColor Cyan
    
    $envTemplate = @"
OPENAI_API_KEY=sk-sua-chave-da-openai-aqui
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
"@
    
    Set-Content -Path $envPath -Value $envTemplate
    Write-Host "✅ Arquivo backend\.env criado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔑 ATENÇÃO: Você precisa adicionar sua OpenAI API Key!" -ForegroundColor Yellow
    Write-Host "   1. Pegue sua chave em: https://platform.openai.com/api-keys" -ForegroundColor White
    Write-Host "   2. Edite o arquivo: notepad backend\.env" -ForegroundColor White
    Write-Host "   3. Substitua 'sk-sua-chave-da-openai-aqui' pela chave real" -ForegroundColor White
    Write-Host ""
    $openNotepad = Read-Host "Deseja abrir o notepad agora? (s/n)"
    if ($openNotepad -eq "s") {
        notepad $envPath
        Write-Host "⏳ Aguardando você salvar e fechar o notepad..." -ForegroundColor Yellow
        Read-Host "Pressione Enter quando terminar"
    }
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "              TESTE 1: BACKEND (FastAPI)                      " -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔧 Verificando dependências do backend..." -ForegroundColor Yellow
$requirementsPath = "backend\requirements.txt"
if (Test-Path $requirementsPath) {
    Write-Host "✅ requirements.txt encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ requirements.txt não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Iniciando Backend..." -ForegroundColor Yellow
Write-Host "   URL: http://localhost:8000" -ForegroundColor White
Write-Host "   Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "⏱️  Aguarde 5 segundos para o servidor iniciar..." -ForegroundColor Yellow
Write-Host ""

# Iniciar backend em background
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    cd backend
    & .\venv\Scripts\python.exe main.py
}

Start-Sleep -Seconds 5

# Testar se backend está rodando
Write-Host "🧪 Testando conexão com o backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -Method GET -TimeoutSec 5
    $json = $response.Content | ConvertFrom-Json
    Write-Host "✅ Backend ONLINE!" -ForegroundColor Green
    Write-Host "   Status: $($json.status)" -ForegroundColor White
    Write-Host "   Versão: $($json.version)" -ForegroundColor White
} catch {
    Write-Host "❌ Backend não respondeu" -ForegroundColor Red
    Write-Host "   Verifique os logs acima para erros" -ForegroundColor Yellow
    Stop-Job $backendJob
    Remove-Job $backendJob
    exit 1
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "              TESTE 2: FRONTEND (Next.js)                     " -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "🚀 Iniciando Frontend..." -ForegroundColor Yellow
Write-Host "   URL: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "⏱️  Aguarde 10 segundos para o Next.js compilar..." -ForegroundColor Yellow
Write-Host ""

# Iniciar frontend em background
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    cd frontend
    npm run dev 2>&1 | Out-Null
}

Start-Sleep -Seconds 10

# Testar se frontend está rodando
Write-Host "🧪 Testando conexão com o frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 5
    Write-Host "✅ Frontend ONLINE!" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend não respondeu" -ForegroundColor Red
    Stop-Job $backendJob
    Stop-Job $frontendJob
    Remove-Job $backendJob
    Remove-Job $frontendJob
    exit 1
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "               ✅ TUDO FUNCIONANDO! ✅                        " -ForegroundColor Green
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "🎉 PARABÉNS! Seu Taze AI está rodando!" -ForegroundColor Magenta
Write-Host ""
Write-Host "📊 URLs Disponíveis:" -ForegroundColor Cyan
Write-Host "   • Dashboard:    http://localhost:3000" -ForegroundColor White
Write-Host "   • API Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   • API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

Write-Host "🧪 O que testar agora:" -ForegroundColor Cyan
Write-Host "   1. Abra http://localhost:3000 no navegador" -ForegroundColor White
Write-Host "   2. Clique em uma ação da tabela (ex: PETR4)" -ForegroundColor White
Write-Host "   3. Veja o gráfico e a análise de IA" -ForegroundColor White
Write-Host "   4. Clique no botão roxo (chat) no canto direito" -ForegroundColor White
Write-Host "   5. Pergunte algo: 'Qual ação você recomenda?'" -ForegroundColor White
Write-Host ""

Write-Host "💡 Para ver os logs em tempo real:" -ForegroundColor Yellow
Write-Host "   • Backend:  Receive-Job $($backendJob.Id)" -ForegroundColor White
Write-Host "   • Frontend: Receive-Job $($frontendJob.Id)" -ForegroundColor White
Write-Host ""

Write-Host "🛑 Para parar os servidores:" -ForegroundColor Yellow
Write-Host "   Stop-Job $($backendJob.Id), $($frontendJob.Id)" -ForegroundColor White
Write-Host "   Remove-Job $($backendJob.Id), $($frontendJob.Id)" -ForegroundColor White
Write-Host ""

Write-Host "Pressione QUALQUER TECLA para abrir o dashboard no navegador..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Abrir navegador
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "🌐 Navegador aberto!" -ForegroundColor Green
Write-Host ""
Write-Host "Os servidores continuarão rodando em background." -ForegroundColor Yellow
Write-Host "Para parar, execute: Stop-Job $($backendJob.Id), $($frontendJob.Id)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Divirta-se! 🚀" -ForegroundColor Magenta

