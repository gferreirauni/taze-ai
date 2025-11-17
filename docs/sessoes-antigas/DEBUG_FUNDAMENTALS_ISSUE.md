# 🔍 DEBUG: Fundamentals Não Sendo Enviados

**Data:** 17 de Novembro de 2025  
**Problema:** Buy & Hold mostra score 0.0 com mensagem "Não há dados fundamentalistas disponíveis"

---

## 🐛 PROBLEMA IDENTIFICADO

### **Sintoma:**
- Buy & Hold Score: **0.0/10** - "Fraco"
- Mensagem: "Não há dados fundamentalistas disponíveis para realizar uma análise de Buy & Hold..."
- Swing Trade funcionando corretamente (usa apenas histórico de preços)

### **Causa Raiz:**
Os dados fundamentalistas não estão chegando ao OpenAI GPT-4o, resultando em análise sem dados de P/L, ROE, Dividend Yield, etc.

---

## 🔍 LOGS DE DEBUG ADICIONADOS

### **1. Frontend (`AIInsights.tsx`)**

**Localização:** Função `generateAnalysis()` (linha 64-68)

**Logs Adicionados:**
```typescript
console.log('[AI DEBUG] Stock completo:', stock)
console.log('[AI DEBUG] Fundamentals:', stock.fundamentals)
console.log('[AI DEBUG] Fundamentals existe?', !!stock.fundamentals)
console.log('[AI DEBUG] Fundamentals vazio?', stock.fundamentals && Object.keys(stock.fundamentals).length === 0)
console.log('[AI DEBUG] Payload enviado:', payload)
console.log('[AI DEBUG] Fundamentals no payload:', payload.fundamentals)
console.log('[AI DEBUG] Resposta recebida:', data)
```

**O que verificar:**
- ✅ Se `stock.fundamentals` existe
- ✅ Se `stock.fundamentals` está vazio ({})
- ✅ Quantas keys tem em `fundamentals`
- ✅ Se o payload está sendo enviado corretamente

---

### **2. Backend (`main.py`) - Endpoint `/api/ai/analyze`**

**Localização:** Função `analyze_stock()` (linha 1147-1152)

**Logs Adicionados:**
```python
print(f"\n[AI DEBUG] === Recebido request para {request.symbol} ===")
print(f"[AI DEBUG] Fundamentals recebido? {request.fundamentals is not None}")
print(f"[AI DEBUG] Fundamentals vazio? {request.fundamentals == {} if request.fundamentals else 'None'}")
if request.fundamentals:
    print(f"[AI DEBUG] Keys dos fundamentals: {list(request.fundamentals.keys())[:10]}")
    print(f"[AI DEBUG] Total de indicadores: {len(request.fundamentals)}")
```

**O que verificar:**
- ✅ Se `request.fundamentals` é `None`
- ✅ Se `request.fundamentals` é um dicionário vazio `{}`
- ✅ Quantos indicadores estão presentes
- ✅ Quais são as keys (ex: `indicators_pl`, `indicators_div_yield`)

---

### **3. Backend (`main.py`) - Função `get_aggregated_stock_data()`**

**Localização:** Processamento de fundamentals (linha 153-157)

**Logs Adicionados:**
```python
if fundamentals:
    print(f"[TRADEBOX] ✅ Fundamentals recebidos para {symbol}: {len(fundamentals)} indicadores")
    print(f"[TRADEBOX] Primeiros indicadores: {list(fundamentals.keys())[:5]}")
else:
    print(f"[TRADEBOX] ⚠️ FUNDAMENTALS VAZIOS para {symbol}!")
```

**O que verificar:**
- ✅ Se a API Tradebox está retornando fundamentals
- ✅ Quantos indicadores estão sendo recebidos
- ✅ Quais são os primeiros 5 indicadores

---

## 🧪 COMO TESTAR

### **1. Reiniciar Backend**

```powershell
cd backend
# Se já está rodando: Ctrl+C para parar
.\venv\Scripts\Activate.ps1
python main.py
```

**Observar logs ao iniciar:**
```
[ATUALIZANDO] Cache expirado, buscando dados da Tradebox API...
[TRADEBOX] ✅ Fundamentals recebidos para PETR4: 45 indicadores
[TRADEBOX] Primeiros indicadores: ['indicators_pl', 'indicators_div_yield', ...]
```

---

### **2. Reiniciar Frontend**

```powershell
cd frontend
# Se já está rodando: Ctrl+C para parar
npm run dev
```

**Acessar:** http://localhost:3000/analises

---

### **3. Gerar Análise e Ver Logs**

1. Selecionar **VALE3** (ou qualquer ação)
2. Abrir **DevTools Console** (F12)
3. Clicar em **"Gerar Análise"**

**Logs esperados no Console (Frontend):**
```
[AI DEBUG] Stock completo: { symbol: "VALE3", fundamentals: {...}, ... }
[AI DEBUG] Fundamentals: { indicators_pl: 8.5, indicators_div_yield: 5.2, ... }
[AI DEBUG] Fundamentals existe? true
[AI DEBUG] Fundamentals vazio? false
[AI DEBUG] Payload enviado: { symbol: "VALE3", fundamentals: {...}, ... }
[AI DEBUG] Fundamentals no payload: { indicators_pl: 8.5, ... }
```

**Logs esperados no Terminal (Backend):**
```
[AI DEBUG] === Recebido request para VALE3 ===
[AI DEBUG] Fundamentals recebido? True
[AI DEBUG] Fundamentals vazio? False
[AI DEBUG] Keys dos fundamentals: ['indicators_pl', 'indicators_div_yield', 'indicators_roe', ...]
[AI DEBUG] Total de indicadores: 45
[AI] Gerando análise REAL para VALE3 usando GPT-4o...
[AI] Análise gerada com sucesso para VALE3
[AI] Scores: Buy&Hold=7.5, SwingTrade=8.2
```

---

## 🎯 POSSÍVEIS CAUSAS E SOLUÇÕES

### **Causa 1: API Tradebox Não Retorna Fundamentals**

**Sintoma:**
```
[TRADEBOX] ⚠️ FUNDAMENTALS VAZIOS para PETR4!
```

**Solução:**
- Verificar credenciais da API Tradebox em `backend/.env`
- Verificar se o endpoint `/assetFundamentals/{symbol}` está funcionando
- Verificar se a API retorna `{"data": [{...}]}`

**Teste Manual:**
```bash
curl -u "TradeBox:TradeBoxAI@2025" \
  https://api.tradebox.com.br/v1/assetFundamentals/PETR4
```

---

### **Causa 2: Fundamentals Vazios no Frontend**

**Sintoma:**
```
[AI DEBUG] Fundamentals: {}
[AI DEBUG] Fundamentals vazio? true
```

**Solução:**
- Verificar se `data.stocks` no frontend está recebendo `fundamentals`
- Verificar se o cache do backend tem fundamentals
- Limpar cache do backend: Reiniciar o servidor Python

---

### **Causa 3: Fundamentals Não Chegam ao Backend**

**Sintoma:**
```
[AI DEBUG] Fundamentals recebido? False
```

**Solução:**
- Verificar se `AIInsights` está enviando `stock.fundamentals` corretamente
- Verificar se o payload JSON está correto
- Verificar se não há erro de serialização JSON

---

### **Causa 4: OpenAI Não Recebe Fundamentals**

**Sintoma:**
- Buy & Hold score 0.0
- Mensagem "Não há dados fundamentalistas disponíveis..."

**Solução:**
- Verificar se `generate_real_ai_analysis` está recebendo `fundamentals`
- Verificar se o `user_prompt` inclui `fundamentals` no JSON
- Verificar se OpenAI está processando corretamente

---

## 📝 CHECKLIST DE VALIDAÇÃO

Após adicionar os logs, verificar:

### **Backend Startup:**
- [ ] Logs mostram fundamentals sendo carregados
- [ ] Número de indicadores > 0 (ex: 45 indicadores)
- [ ] Primeiras keys incluem `indicators_pl`, `indicators_div_yield`, etc.

### **Frontend Request:**
- [ ] Console mostra `fundamentals` com dados
- [ ] `fundamentals` não está vazio ({})
- [ ] Payload inclui `fundamentals` completo

### **Backend Receive:**
- [ ] Logs mostram `Fundamentals recebido? True`
- [ ] Logs mostram total de indicadores > 0
- [ ] Keys incluem indicadores esperados

### **AI Analysis:**
- [ ] Buy & Hold score > 0
- [ ] Buy & Hold summary menciona P/L, ROE, etc.
- [ ] Não mostra mensagem de "dados não disponíveis"

---

## 🔧 PRÓXIMOS PASSOS

1. **Reiniciar backend e frontend**
2. **Gerar uma análise** e observar logs
3. **Identificar onde os fundamentals são perdidos**
4. **Aplicar correção específica** baseada nos logs

---

## 📊 EXEMPLO DE LOGS CORRETOS

### **Backend Startup:**
```
[TRADEBOX] ✅ Fundamentals recebidos para PETR4: 45 indicadores
[TRADEBOX] Primeiros indicadores: ['indicators_pl', 'indicators_div_yield', 'indicators_roe', 'indicators_pvp', 'indicators_debt_equity']
```

### **Frontend Console:**
```
[AI DEBUG] Fundamentals: {
  indicators_pl: 8.5,
  indicators_div_yield: 5.2,
  indicators_roe: 18.5,
  ... (40+ mais)
}
[AI DEBUG] Fundamentals existe? true
[AI DEBUG] Fundamentals vazio? false
```

### **Backend Request:**
```
[AI DEBUG] === Recebido request para PETR4 ===
[AI DEBUG] Fundamentals recebido? True
[AI DEBUG] Fundamentals vazio? False
[AI DEBUG] Keys dos fundamentals: ['indicators_pl', 'indicators_div_yield', 'indicators_roe', ...]
[AI DEBUG] Total de indicadores: 45
```

### **AI Response:**
```
[AI] Gerando análise REAL para PETR4 usando GPT-4o...
[AI] Análise gerada com sucesso para PETR4
[AI] Scores: Buy&Hold=7.5, SwingTrade=8.2
```

---

## ✅ STATUS

**Logs adicionados em:**
1. ✅ `frontend/components/dashboard/AIInsights.tsx` (linha 64-80)
2. ✅ `backend/main.py` - endpoint `/api/ai/analyze` (linha 1147-1152)
3. ✅ `backend/main.py` - função `get_aggregated_stock_data()` (linha 153-157)

**Próximo passo:**
- Reiniciar ambos servidores
- Gerar análise
- Verificar logs para identificar onde os dados são perdidos

---

**Desenvolvido com 🔍 pela equipe Taze AI**  
**"Debugging is the art of removing bugs. Programming is the art of adding them."**

