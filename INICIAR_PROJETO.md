# 🚀 GUIA RÁPIDO: Como Iniciar o Taze AI

## ⚡ Início Rápido (5 minutos)

### 1️⃣ Configurar OpenAI API Key (OBRIGATÓRIO para o Chat)

**Opção A - Criar arquivo .env manualmente:**
```powershell
cd backend
notepad .env
```

**Cole isto no arquivo:**
```
OPENAI_API_KEY=sk-sua-chave-da-openai-aqui
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

**Salve e feche** (Ctrl+S, Alt+F4)

**Opção B - Via PowerShell:**
```powershell
cd backend
Set-Content -Path .env -Value "OPENAI_API_KEY=sk-sua-chave-aqui`nAPI_HOST=0.0.0.0`nAPI_PORT=8000`nENVIRONMENT=development"
```

⚠️ **Substitua** `sk-sua-chave-aqui` pela sua chave real da OpenAI
🔑 **Não tem chave?** Pegue em: https://platform.openai.com/api-keys

---

### 2️⃣ Instalar Dependências do Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Você verá:**
```
Installing collected packages: fastapi, uvicorn, pandas, openai, python-dotenv...
Successfully installed fastapi-0.115.0 uvicorn-0.32.0 ...
```

---

### 3️⃣ Iniciar o Backend

**Terminal 1 (PowerShell):**
```powershell
# Volte para raiz do projeto
cd ..

# Execute o script de início
.\start-backend.ps1
```

**OU manualmente:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

**✅ Você verá:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**🎉 Backend ONLINE!** → http://localhost:8000

---

### 4️⃣ Iniciar o Frontend

**Terminal 2 (PowerShell) - NOVO TERMINAL:**
```powershell
# Navegue até o projeto
cd C:\Users\Gustavo\OneDrive\Desktop\tazeai

# Execute o script
.\start-frontend.ps1
```

**OU manualmente:**
```powershell
cd frontend
npm run dev
```

**✅ Você verá:**
```
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000

✓ Ready in 2.5s
```

**🎉 Frontend ONLINE!** → http://localhost:3000

---

## 🧪 COMO TESTAR CADA FUNCIONALIDADE

### ✅ Teste 1: Backend Funcionando

**Abra:** http://localhost:8000

**Você deve ver:**
```json
{
  "message": "Bem-vindo à Taze AI API! 🚀",
  "status": "online",
  "version": "1.0.0"
}
```

**Documentação da API:** http://localhost:8000/docs

---

### ✅ Teste 2: Dashboard Principal

**Abra:** http://localhost:3000

**Você deve ver:**
- 🎨 Fundo escuro (dark mode)
- 📊 Sidebar esquerda com logo "TazeAI"
- 💰 3 cards no topo (Patrimônio, Rentabilidade, Ações)
- 📈 Gráfico de linha (primeira ação)
- 🤖 Card de "Análise de IA" ao lado do gráfico
- 📋 Tabela com 5 ações (PETR4, VALE3, ITUB4, WEGE3, BBAS3)

---

### ✅ Teste 3: Seleção de Ações

**Ação:** Clique em qualquer ação da tabela (ex: VALE3)

**O que acontece:**
1. ⏳ Linha fica destacada (borda verde)
2. 📈 Gráfico atualiza com histórico da VALE3
3. 🤖 "Analisando VALE3 com IA..." (skeleton loader)
4. ⏱️ Após 1.5s: Análise completa aparece
5. 🎯 Badge colorido: COMPRA/MANTER/VENDA

---

### ✅ Teste 4: Análise de IA (Mockada)

**No card "Análise de IA":**

**Você verá:**
- 🤖 Ícone gradiente roxo-rosa
- 📊 Badge de recomendação (verde/vermelho/laranja)
- 📝 Análise completa em markdown
- 💼 Contexto do setor
- 🔄 Botão "Atualizar Análise"
- 📄 Botão "Relatório Completo"

**Teste:** Clique em "Atualizar Análise" → Nova análise é gerada!

---

### ✅ Teste 5: Chat com GPT-4 (REAL!)

**1. Encontre o botão:**
- 👀 Procure no **canto inferior direito**
- 💜 Botão redondo **roxo-rosa** com ícone de mensagem
- 🟢 Bolinha verde pulsando = Online

**2. Abra o chat:**
- 🖱️ Clique no botão
- 📱 Painel desliza para cima
- 👋 Mensagem de boas-vindas aparece

**3. Teste SEM contexto:**
```
Você: Qual a diferença entre PETR3 e PETR4?
```
**Aguarde 2-3 segundos...**
```
Taze AI: PETR3 são ações ordinárias (ON) que dão direito a voto...
```

**4. Teste COM contexto (selecione uma ação primeiro!):**
```
1. Clique em PETR4 na tabela
2. Abra o chat
3. Note o badge: "Contexto: PETR4 - R$ 38.50"
```

**Pergunte:**
```
Vale a pena comprar?
```

**GPT-4 responderá considerando:**
- ✅ Preço atual (R$ 38.50)
- ✅ Variação (+2.34%)
- ✅ Setor (Petróleo e Gás)
- ✅ Contexto completo

---

## 🎬 ROTEIRO DE DEMONSTRAÇÃO (Para os Sócios)

### **Cena 1: Abertura Impactante (30s)**
1. Abra http://localhost:3000
2. Mostre o dark mode elegante
3. "Este é o **Taze AI** - Dashboard inteligente para B3"

### **Cena 2: Visão Geral (1min)**
1. Aponte para os 3 cards: "Patrimônio atualizado em tempo real"
2. Scroll suave pela tabela: "5 ações monitoradas"
3. "Atualização automática a cada 30 segundos"

### **Cena 3: Análise de IA (2min)**
1. Clique em VALE3
2. "Veja como o gráfico atualiza instantaneamente"
3. Aponte para o card de IA: "Analisando..."
4. Quando aparecer: "**Análise automática** com recomendação"
5. Leia em voz alta: "COMPRA - Tendência de alta confirmada..."
6. "Tudo isso **sem intervenção humana**"

### **Cena 4: O Diferencial - Chat com IA (3min)**
1. Clique no botão roxo
2. "Agora o **verdadeiro diferencial**..."
3. Digite: "Qual ação você recomenda para dividendos?"
4. Enquanto o GPT-4 responde: "Usamos **OpenAI GPT-4** - a mesma IA do ChatGPT"
5. Leia a resposta em voz alta
6. "Mas tem mais..." → Clique em PETR4 na tabela
7. Mostre o badge de contexto: "A IA **sabe** qual ação estou vendo"
8. Pergunte: "Vale a pena comprar?"
9. "Viu? Resposta **personalizada** para esta ação específica"

### **Cena 5: Fechamento (1min)**
1. "Nosso diferencial:"
   - ✅ Dashboard bonito? Tem.
   - ✅ Dados em tempo real? Tem.
   - ✅ Análise automática? Tem.
   - ✅ **Chat inteligente com IA?** **TEMOS!**
2. "Enquanto a concorrência mostra só gráficos..."
3. "Nós temos um **analista financeiro 24/7 dentro do app**"
4. "Pronto para **escalar** e conquistar o mercado!"

---

## 🐛 Problemas Comuns e Soluções

### ❌ Backend não inicia

**Erro:** `ModuleNotFoundError: No module named 'fastapi'`

**Solução:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### ❌ Chat retorna erro

**Erro:** `Incorrect API key provided`

**Solução:**
1. Verifique o arquivo `.env`:
```powershell
cd backend
Get-Content .env
```
2. Certifique-se que a chave começa com `sk-`
3. Reinicie o backend

**Erro:** `You exceeded your current quota`

**Solução:**
- Sua conta OpenAI não tem créditos
- Adicione créditos: https://platform.openai.com/account/billing
- **OU** troque para GPT-3.5 (mais barato) no `backend/main.py` linha 425:
```python
model="gpt-3.5-turbo",  # Ao invés de gpt-4o
```

---

### ❌ Frontend não conecta ao Backend

**Sintoma:** Cards carregam mas não mostram dados

**Solução:**
1. Verifique se backend está rodando: http://localhost:8000
2. Verifique CORS no `backend/main.py` linha 24:
```python
allow_origins=["http://localhost:3000"]
```

---

### ❌ Gráfico não aparece

**Solução:**
```powershell
cd frontend
npm install recharts
npm run dev
```

---

## 📊 Checklist de Testes Completo

### Backend
- [ ] http://localhost:8000 retorna JSON
- [ ] http://localhost:8000/docs abre Swagger UI
- [ ] GET /api/stocks retorna 5 ações
- [ ] POST /api/ai/analyze funciona
- [ ] POST /api/ai/chat responde (se configurado)

### Frontend
- [ ] http://localhost:3000 abre o dashboard
- [ ] Dark mode está aplicado
- [ ] 3 cards aparecem com valores
- [ ] Gráfico renderiza
- [ ] Tabela mostra 5 ações
- [ ] Clicar em ação atualiza gráfico
- [ ] Card de IA mostra análise
- [ ] Botão de chat aparece no canto
- [ ] Chat abre e responde

---

## 🎯 Está Pronto!

**URLs Importantes:**
- 🖥️ **Dashboard:** http://localhost:3000
- 🔧 **API:** http://localhost:8000
- 📚 **Docs API:** http://localhost:8000/docs
- 🐙 **GitHub:** https://github.com/gferreirauni/taze-ai

**Documentação:**
- 📖 `README.md` - Overview geral
- 🚀 `COMO_EXECUTAR_MVP.md` - Guia de execução
- 🔑 `CONFIGURAR_OPENAI.md` - Setup da OpenAI
- 🎯 `NEXT_STEPS.md` - Próximas melhorias
- 📂 `ESTRUTURA_DO_PROJETO.md` - Arquitetura

---

**Divirta-se! 🎉** Qualquer dúvida, consulte os arquivos `.md` na raiz do projeto!

