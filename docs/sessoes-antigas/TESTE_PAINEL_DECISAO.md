# 🧪 Guia de Teste - Painel de Decisão

**Versão:** v2.3.1  
**Data:** 17 de Novembro de 2025

---

## 🚀 Como Testar

### 1️⃣ Iniciar Backend e Frontend

```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Aguardar:**
- Backend: `Uvicorn running on http://0.0.0.0:8000`
- Frontend: `ready started server on http://localhost:3000`

---

## 🎯 Teste 1: Homepage com Análises em Cache

### **Objetivo:** Verificar se cards carregam análises automaticamente

### **Passos:**

1. **Abrir:** http://localhost:3000

2. **Verificar Header:**
   - ✅ Título: "Painel de Decisão Taze AI"
   - ✅ Subtítulo: "Análises de IA para os principais ativos..."
   - ✅ Emojis: 🏛️ Buy & Hold • 📈 Swing Trade • ⚡ Day Trade

3. **Verificar Grid:**
   - ✅ 5 cards visíveis (PETR4, BBAS3, VALE3, MGLU3, WEGE3)
   - ✅ Layout: 2 colunas (desktop) ou 1 coluna (mobile)

4. **Verificar Contador:**
   - ✅ "X de 5 com análise de IA"
   - Se X = 0: Nenhuma análise em cache (normal na primeira vez)
   - Se X > 0: Análises disponíveis!

---

## 🎯 Teste 2: Card SEM Análise

### **Objetivo:** Verificar estado vazio (call-to-action)

### **Passos:**

1. **Localizar card sem análise** (provavelmente todos na primeira vez)

2. **Verificar elementos:**
   - ✅ Símbolo + Nome (ex: PETR4 - Petrobras PN)
   - ✅ Preço atual (ex: R$ 38.49)
   - ✅ Variação diária (ex: +0.65%)
   - ✅ Ícone de TrendingUp (📈)
   - ✅ Texto: "Clique para gerar análise de IA"
   - ✅ Subtexto: "3 perfis: Buy & Hold • Swing Trade • Day Trade"

3. **Testar hover:**
   - ✅ Borda fica roxa
   - ✅ Cursor muda para pointer

4. **Clicar no card:**
   - ✅ Redireciona para `/analises?ticker=PETR4`
   - ✅ Ação já vem selecionada

---

## 🎯 Teste 3: Gerar Análise

### **Objetivo:** Gerar análise de IA para uma ação

### **Passos:**

1. **Já na página /analises?ticker=PETR4**

2. **Verificar:**
   - ✅ PETR4 selecionada na lista
   - ✅ Gráfico visível
   - ✅ Seção "Análise de IA" visível

3. **Clicar em "Gerar Análise"**

4. **Aguardar 10-15 segundos:**
   - ✅ Loading: Bot animado
   - ✅ Texto: "Analisando PETR4 com IA..."

5. **Verificar resultado:**
   - ✅ Badge de recomendação (COMPRA FORTE/COMPRA/MANTER/VENDA)
   - ✅ 3 cards verticais:
     - 🏛️ Buy & Hold (Landmark, verde)
     - 📈 Swing Trade (TrendingUp, azul)
     - ⚡ Day Trade (Zap, amarelo)
   - ✅ Scores entre 0.0 e 10.0
   - ✅ Sumários completos (1-2 frases cada)

6. **Verificar logs do backend:**
   ```
   [AI] Gerando análise TRIPLA para PETR4
   [AI] Scores: Buy&Hold=X.X, SwingTrade=Y.Y, DayTrade=Z.Z
   [AI CACHE] Análise TRIPLA gerada e armazenada: PETR4_2025-11-17
   ```

---

## 🎯 Teste 4: Card COM Análise (Homepage)

### **Objetivo:** Verificar se card exibe análise após geração

### **Passos:**

1. **Voltar à homepage:** http://localhost:3000

2. **Localizar card PETR4** (agora deve ter análise)

3. **Verificar elementos:**
   - ✅ Recomendação no topo (badge colorido)
   - ✅ Grid de 3 colunas com scores:
     - 🏛️ Warren (Buy & Hold)
     - 📈 Trader (Swing Trade)
     - ⚡ Viper (Day Trade)
   - ✅ Labels de qualidade (Excelente/Bom/Razoável/Fraco)
   - ✅ 3 sumários com emojis:
     - 🏛️ Fundamentalista: ...
     - 📈 Técnico: ...
     - ⚡ Volatilidade: ...
   - ✅ Botão "Ver Análise Completa →"
   - ✅ Hora de geração (ex: "Gerada em: 14:30")

4. **Verificar contador:**
   - ✅ "1 de 5 com análise de IA" (se apenas PETR4 foi gerada)

---

## 🎯 Teste 5: Link para Análise Completa

### **Objetivo:** Verificar se link funciona

### **Passos:**

1. **No card PETR4 (com análise):**
2. **Clicar em "Ver Análise Completa →"**
3. **Verificar:**
   - ✅ Redireciona para `/analises?ticker=PETR4`
   - ✅ PETR4 já está selecionada
   - ✅ Análise de IA já carregada (cache!)
   - ✅ Badge verde: "Análise do dia em cache"

---

## 🎯 Teste 6: Responsividade

### **Objetivo:** Verificar layout mobile

### **Passos:**

1. **Abrir DevTools:** F12
2. **Ativar modo mobile:** Ícone de celular 📱
3. **Redimensionar tela para 375px (iPhone)**

4. **Verificar homepage:**
   - ✅ Cards empilhados verticalmente (1 coluna)
   - ✅ Grid de scores: ainda 3 colunas (compacto)
   - ✅ Sumários legíveis
   - ✅ Botão "Ver Análise Completa" não quebra

5. **Verificar página de análises:**
   - ✅ AIInsights: 3 cards verticais
   - ✅ Gráfico responsivo
   - ✅ Lista de ações esconde/colapsa

---

## 🎯 Teste 7: Gerar Múltiplas Análises

### **Objetivo:** Popular o cache com 3+ análises

### **Passos:**

1. **Gerar análise para PETR4** (já feito)
2. **Gerar análise para BBAS3:**
   - Ir para `/analises?ticker=BBAS3`
   - Clicar "Gerar Análise"
   - Aguardar resultado

3. **Gerar análise para VALE3:**
   - Ir para `/analises?ticker=VALE3`
   - Clicar "Gerar Análise"
   - Aguardar resultado

4. **Voltar à homepage:**
   - ✅ Contador: "3 de 5 com análise de IA"
   - ✅ 3 cards com análises completas
   - ✅ 2 cards com call-to-action

---

## 🎯 Teste 8: Cache de 24h

### **Objetivo:** Verificar se análise persiste

### **Passos:**

1. **Fechar o navegador**
2. **Reabrir:** http://localhost:3000
3. **Verificar:**
   - ✅ Cards com análises ainda exibem os scores
   - ✅ Não precisa gerar novamente
   - ✅ Hora de geração é a mesma da primeira vez

**Nota:** Cache expira após 24h ou ao reiniciar o backend.

---

## 📋 Checklist Completo

### **Homepage:**
- [ ] Título e subtítulo corretos
- [ ] 5 ações visíveis
- [ ] Grid responsivo (2 colunas desktop, 1 mobile)
- [ ] Contador "X de 5" correto
- [ ] Seção de notícias visível

### **Card SEM Análise:**
- [ ] Preço e variação visíveis
- [ ] Ícone TrendingUp (📈)
- [ ] Call-to-action claro
- [ ] Hover funciona
- [ ] Link redireciona para /analises

### **Card COM Análise:**
- [ ] Recomendação visível
- [ ] 3 scores em grid
- [ ] Ícones corretos (🏛️📈⚡)
- [ ] Nomes dos analistas (Warren, Trader, Viper)
- [ ] 3 sumários completos
- [ ] Botão funcional
- [ ] Hora de geração visível

### **Página de Análises:**
- [ ] URL com ?ticker funciona
- [ ] Seleção automática da ação
- [ ] Gráfico carrega
- [ ] AIInsights com 3 cards verticais
- [ ] Geração de análise funciona
- [ ] Cache funciona (badge verde)

### **Backend:**
- [ ] API /api/stocks retorna 5 ações
- [ ] API /api/ai/analysis/{symbol} retorna cache
- [ ] Logs mostram "análise TRIPLA"
- [ ] 3 scores no log (Buy&Hold, Swing, Day)
- [ ] Cache persiste por 24h

---

## 🐛 Problemas Comuns

### ❌ Cards não exibem análises

**Causa:** Cache vazio  
**Solução:** Gerar análise manualmente em `/analises`

### ❌ Score de Day Trade aparece NaN

**Causa:** Backend não retorna dayTradeScore  
**Solução:** Verificar backend (linha 1126 do main.py)

### ❌ Grid de scores quebrado

**Causa:** CSS não aplicado  
**Solução:** Verificar Tailwind CSS (`grid grid-cols-3`)

### ❌ Link não funciona

**Causa:** useRouter não importado  
**Solução:** Usar `<Link href={...}>` do Next.js

### ❌ Contador sempre "0 de 5"

**Causa:** ai_analysis não está sendo atribuído  
**Solução:** Verificar fetch de análises (linha 56-71 do page.tsx)

---

## ✅ Resultado Esperado

**Homepage:**
- Grid de 2 colunas com 5 cards
- Cards com análises mostram 3 scores completos
- Cards sem análises mostram call-to-action
- Contador preciso
- Notícias abaixo

**UX:**
- Valor da IA visível **imediatamente**
- Navegação fluida entre páginas
- Links funcionais
- Loading states claros

---

## 📞 Próximos Passos

1. ✅ Testar com todas as 5 ações
2. ✅ Verificar se cache de 24h funciona
3. ✅ Validar responsividade mobile
4. ✅ Confirmar que logs estão corretos
5. ✅ Compartilhar feedback!

**Dúvidas?** Consulte `PAINEL_DECISAO_HOMEPAGE.md` para detalhes técnicos.

---

**Boa sorte nos testes! 🚀**

