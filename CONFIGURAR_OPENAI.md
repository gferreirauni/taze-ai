# 🔑 Como Configurar a OpenAI API Key

## 📝 Passo a Passo

### 1. Obter sua API Key da OpenAI

1. Acesse https://platform.openai.com/api-keys
2. Faça login na sua conta OpenAI
3. Clique em **"Create new secret key"**
4. Copie a chave (começa com `sk-...`)
5. **IMPORTANTE**: Salve em um lugar seguro, ela só aparece uma vez!

### 2. Configurar no Backend

**Windows (PowerShell):**
```powershell
cd backend
echo OPENAI_API_KEY=sk-sua-chave-aqui > .env
```

**Ou crie manualmente:**
1. Abra a pasta `backend/`
2. Crie um arquivo chamado `.env` (sem nome antes do ponto)
3. Cole este conteúdo:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-sua-chave-aqui

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Environment
ENVIRONMENT=development
```

4. Substitua `sk-sua-chave-aqui` pela sua chave real da OpenAI

### 3. Verificar Configuração

**Testar se o arquivo existe:**
```powershell
cd backend
Get-Content .env
```

Você deve ver sua chave configurada.

### 4. Reiniciar o Backend

```powershell
# Se o backend estiver rodando, pare (Ctrl+C)
# Depois inicie novamente:
.\start-backend.ps1

# Ou manualmente:
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

## ✅ Verificar se Está Funcionando

1. **Backend iniciado**: http://localhost:8000/docs
2. **Frontend rodando**: http://localhost:3000
3. **Clique no botão de chat** (canto inferior direito - ícone roxo/rosa)
4. **Digite uma mensagem**: "Qual ação você recomenda hoje?"
5. **Se funcionar**: Você verá uma resposta do GPT-4! 🎉

## ❌ Problemas Comuns

### Erro: "Incorrect API key provided"
**Solução**: Verifique se você copiou a chave completa (começa com `sk-`)

### Erro: "You exceeded your current quota"
**Solução**: Sua conta OpenAI não tem créditos. Adicione créditos em:
https://platform.openai.com/account/billing

### Arquivo .env não existe
**Solução**: 
```powershell
cd backend
New-Item -Path .env -ItemType File
# Depois edite com notepad:
notepad .env
```

### Backend não carrega o .env
**Solução**: 
1. Verifique se `python-dotenv` está instalado:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install python-dotenv
```
2. Reinicie o backend

## 💰 Custos da OpenAI

### GPT-4o (Modelo Atual)
- **Input**: $2.50 por 1M tokens
- **Output**: $10.00 por 1M tokens

### Estimativa de Uso:
- **Por mensagem**: ~0.01 - 0.03 USD
- **100 mensagens**: ~$1-3 USD
- **1000 mensagens**: ~$10-30 USD

### Para Economizar:
No arquivo `backend/main.py`, linha 425, troque:
```python
model="gpt-4o",  # Atual (mais caro, melhor)
```
Para:
```python
model="gpt-3.5-turbo",  # Mais barato (10x menos)
```

**GPT-3.5-turbo**: $0.50 por 1M tokens (input) / $1.50 por 1M tokens (output)

## 🔒 Segurança

⚠️ **NUNCA** compartilhe sua API key!
⚠️ **NUNCA** faça commit do arquivo `.env` no GitHub!

O `.gitignore` já está configurado para ignorar `.env`, mas sempre verifique antes de fazer push.

## 🚀 Pronto!

Agora você pode conversar com o **Taze AI Assistant** em tempo real! 🤖💬

Ele vai:
- ✅ Analisar ações da B3
- ✅ Responder perguntas sobre investimentos
- ✅ Usar contexto da ação que você está vendo
- ✅ Dar recomendações personalizadas

**Divirta-se!** 🎉

