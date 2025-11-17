# 🧪 Guia de Teste - Análise Tripla (3 Perfis)

**Versão:** v2.3.0  
**Data:** 17 de Novembro de 2025

---

## ✅ O Que Foi Alterado?

### Backend
- ✅ B3_STOCKS agora é: `["PETR4", "BBAS3", "VALE3", "MGLU3", "WEGE3"]`
- ✅ System prompt com **3 analistas** (Warren, Trader, Viper)
- ✅ API retorna **3 scores** (Buy & Hold, Swing Trade, Day Trade)

### Frontend
- ✅ **3 cards** em vez de 2
- ✅ Novos ícones: 🏛️ Landmark, 📈 TrendingUp, ⚡ Zap
- ✅ Layout responsivo (3 colunas no desktop, 1 no mobile)

---

## 🚀 Como Testar

### 1️⃣ Iniciar o Backend

```bash
cd backend
python main.py
```

**Esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2️⃣ Iniciar o Frontend

```bash
cd frontend
npm run dev
```

**Esperado:**
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

### 3️⃣ Testar a Lista de Ações

1. Abrir: http://localhost:3000
2. Verificar lista à esquerda com **5 ações**:
   - ✅ PETR4
   - ✅ BBAS3
   - ✅ VALE3
   - ✅ MGLU3 (nova!)
   - ✅ WEGE3

**❌ Não deve aparecer:** ITUB4 (foi removida)

### 4️⃣ Testar Análise Tripla

1. **Clicar em qualquer ação** (ex: PETR4)
2. Rolar até "Análise de IA"
3. **Clicar em "Gerar Análise"**
4. **Aguardar 10-15 segundos** (IA processando)

**Esperado:**
```
✅ Badge de recomendação (COMPRA FORTE / COMPRA / MANTER / VENDA)
✅ 3 cards lado a lado (desktop) ou empilhados (mobile):
   - 🏛️ Buy & Hold (verde)
   - 📈 Swing Trade (azul)
   - ⚡ Day Trade (amarelo)
✅ Cada card com:
   - Score (0.0 a 10.0)
   - Label (Excelente/Bom/Razoável/Fraco)
   - Sumário da análise (1-2 frases)
```

### 5️⃣ Verificar Logs do Backend

**No terminal do backend, verificar:**

```bash
[AI] Gerando análise TRIPLA para PETR4 (Fundamentals: 15 indicadores)
[AI] Análise gerada com sucesso para PETR4
[AI] Scores: Buy&Hold=7.5, SwingTrade=8.2, DayTrade=6.8
[AI CACHE] Análise TRIPLA gerada e armazenada: PETR4_2025-11-17
```

### 6️⃣ Testar Cache (24h)

1. **Fechar a análise** (voltar à lista)
2. **Abrir a mesma ação novamente**
3. Verificar badge verde:
   > "✅ Análise do dia em cache (economizando tokens)"

**Esperado:** Análise carrega instantaneamente (sem chamar OpenAI)

### 7️⃣ Testar Responsividade

**Desktop (>768px):**
- ✅ 3 cards lado a lado

**Mobile (<768px):**
- ✅ 3 cards empilhados verticalmente

**Como testar:**
- Apertar `F12` no navegador
- Clicar no ícone de celular (📱)
- Redimensionar tela

---

## 🔍 Checklist de Validação

### Backend
- [ ] Backend rodando sem erros
- [ ] Lista tem 5 ações (PETR4, BBAS3, VALE3, MGLU3, WEGE3)
- [ ] Log mostra "análise TRIPLA"
- [ ] Log mostra 3 scores (Buy&Hold, SwingTrade, DayTrade)
- [ ] Cache funcionando (badge verde na segunda chamada)

### Frontend
- [ ] Frontend rodando sem erros de console (F12)
- [ ] 3 cards visíveis (não 2)
- [ ] Ícones corretos (🏛️ Landmark, 📈 TrendingUp, ⚡ Zap)
- [ ] Scores entre 0.0 e 10.0
- [ ] Sumários diferentes para cada perfil
- [ ] Recomendação visível (COMPRA FORTE/COMPRA/MANTER/VENDA)

### Design
- [ ] Cards alinhados horizontalmente (desktop)
- [ ] Cards empilhados verticalmente (mobile)
- [ ] Cores dos scores corretas:
  - 8-10: Verde
  - 6-7: Azul
  - 4-5: Laranja
  - 0-3: Vermelho

---

## 🐛 Problemas Comuns

### ❌ Erro: "Campo obrigatório ausente"

**Causa:** OpenAI não retornou todos os campos  
**Solução:** Verificar logs do backend e retentar

### ❌ Score aparece como NaN

**Causa:** TypeScript recebendo formato errado  
**Solução:** Verificar se backend está retornando `dayTradeScore` (camelCase)

### ❌ Card de Day Trade não aparece

**Causa:** Interface TypeScript não atualizada  
**Solução:** Verificar linhas 21-22 do `AIInsights.tsx`

### ❌ Ação ITUB4 ainda aparece

**Causa:** Cache do backend  
**Solução:** Reiniciar backend (`CTRL+C` e rodar `python main.py` novamente)

---

## 📊 Exemplo de Resultado Esperado

### PETR4 (Exemplo)

**Recomendação:** COMPRA FORTE

**🏛️ Buy & Hold: 7.5 / 10 (Bom)**
> P/L atrativo de 4.2x e dividend yield de 12%. Empresa lucrativa com baixa dívida.

**📈 Swing Trade: 8.2 / 10 (Excelente)**
> Tendência de alta confirmada. Rompeu resistência em R$ 38.50. Próximo alvo: R$ 42.00.

**⚡ Day Trade: 6.8 / 10 (Bom)**
> Volatilidade moderada de 2.1%. Amplitude intraday favorável para operações rápidas.

---

## ✅ Teste Completo Aprovado!

Se todos os itens do checklist estiverem ✅, a implementação está **funcionando perfeitamente**!

---

## 📞 Próximos Passos

1. ✅ Testar com todas as 5 ações
2. ✅ Verificar coerência das análises (suporte < preço < resistência)
3. ✅ Validar cache de 24h (não gastar tokens desnecessariamente)
4. ✅ Compartilhar feedback no chat

**Dúvidas?** Consulte o arquivo `REFINO_ANALISE_MESTRE_3_PERFIS.md` para detalhes técnicos.

---

**Boa sorte nos testes! 🚀**

