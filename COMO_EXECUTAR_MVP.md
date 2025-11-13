# 🚀 Como Executar o MVP do Taze AI

## ⚡ Início Rápido

### 1️⃣ Iniciar o Backend (FastAPI)

**Terminal 1:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

Ou use o script rápido:
```powershell
.\start-backend.ps1
```

✅ Backend rodando em: **http://localhost:8000**  
📚 Documentação da API: **http://localhost:8000/docs**

### 2️⃣ Iniciar o Frontend (Next.js)

**Terminal 2:**
```powershell
cd frontend
npm run dev
```

Ou use o script rápido:
```powershell
.\start-frontend.ps1
```

✅ Frontend rodando em: **http://localhost:3000**

## 🎨 O Que Você Vai Ver

### Dashboard Completo com:
- ✅ **Sidebar** com logo Taze AI e navegação
- ✅ **3 Summary Cards**:
  - Patrimônio Total: R$ 125.478,90
  - Rentabilidade Hoje: +2,34% (R$ 2.876,45)
  - Ações Monitoradas: 5 empresas

- ✅ **Gráfico Interativo** (Recharts):
  - Histórico de 30 dias
  - Linha verde para valorização
  - Linha vermelha para desvalorização
  - Tooltip com detalhes ao passar o mouse

- ✅ **Tabela de Ações**:
  - PETR4 - Petrobras PN (Petróleo e Gás)
  - VALE3 - Vale ON (Mineração)
  - ITUB4 - Itaú Unibanco PN (Financeiro)
  - WEGE3 - WEG ON (Indústria)
  - BBAS3 - Banco do Brasil ON (Financeiro)
  - Clique em qualquer ação para ver o gráfico

## 🎯 Funcionalidades Implementadas

### Backend (FastAPI)
- ✅ Geração de dados mockados realistas
- ✅ Histórico de preços de 30 dias com volatilidade simulada
- ✅ Cálculo automático de variação diária
- ✅ Endpoint `/api/stocks` - Lista todas as ações
- ✅ Endpoint `/api/stocks/{symbol}` - Detalhes de uma ação
- ✅ Endpoint `/api/portfolio/summary` - Resumo da carteira
- ✅ CORS configurado para o frontend

### Frontend (Next.js 14)
- ✅ Dashboard dark mode (bg-zinc-950)
- ✅ Sidebar fixa com logo e menus
- ✅ Cards de resumo com ícones (lucide-react)
- ✅ Gráfico de linha interativo (Recharts)
- ✅ Tabela de ações responsiva
- ✅ Seleção interativa de ações
- ✅ Atualização automática a cada 30 segundos
- ✅ Loading state com spinner
- ✅ Cores dinâmicas (verde para lucro, vermelho para prejuízo)

## 📊 Endpoints da API

### GET /api/stocks
```json
{
  "stocks": [
    {
      "symbol": "PETR4",
      "name": "Petrobras PN",
      "sector": "Petróleo e Gás",
      "currentPrice": 38.50,
      "dailyVariation": 1.25,
      "history": [
        { "date": "2025-10-15", "value": 36.80 },
        ...
      ]
    }
  ],
  "timestamp": "2025-11-13T17:45:00",
  "count": 5
}
```

### GET /api/stocks/PETR4
Retorna detalhes completos incluindo volume e market cap.

### GET /api/portfolio/summary
```json
{
  "totalValue": 125478.90,
  "dailyChange": 2.34,
  "dailyChangeValue": 2876.45,
  "stocksCount": 5
}
```

## 🎨 Tema e Cores

- **Background**: `bg-zinc-950` (#09090b)
- **Cards**: `bg-zinc-900` com `border-zinc-800`
- **Texto**: Branco (`text-white`)
- **Lucro**: Verde (`text-emerald-500`)
- **Prejuízo**: Vermelho (`text-red-500`)
- **Hover**: `hover:bg-zinc-800`

## 🔥 Tecnologias Utilizadas

**Backend:**
- FastAPI 0.115
- Python 3.10+
- Uvicorn (ASGI server)

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Recharts (gráficos)
- Lucide React (ícones)

## 📸 Preview

```
┌─────────────────────────────────────────────────┐
│  Taze AI                                        │
│  Investimentos Inteligentes                     │
├─────────────────────────────────────────────────┤
│  🏠 Dashboard                                    │
│  💼 Carteira                                     │
│  📈 Análises                                     │
│  ⚙️  Configurações                               │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Patrimônio Total        Rentabilidade Hoje    Ações        │
│  R$ 125.478,90          R$ 2.876,45            5            │
│  +2,34%                 +2,34%                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  PETR4 - Petrobras PN                    R$ 38,50           │
│  [Gráfico de linha com 30 dias de histórico]               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Ação      │  Setor           │  Preço    │  Variação      │
│  PETR4     │  Petróleo e Gás  │  R$ 38,50 │  +1,25% 📈     │
│  VALE3     │  Mineração       │  R$ 61,20 │  +0,85% 📈     │
│  ...                                                         │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Próximas Melhorias Sugeridas

1. **Filtros e Buscas**
   - Buscar ações por símbolo
   - Filtrar por setor

2. **Mais Gráficos**
   - Gráfico de pizza para distribuição da carteira
   - Gráfico de barras para comparação

3. **Alertas**
   - Notificações quando preço atinge um valor
   - Alertas de grandes variações

4. **Análise com IA**
   - Integrar GPT-4 para análises
   - Recomendações personalizadas

5. **Autenticação**
   - Login/Registro de usuários
   - Carteiras personalizadas

## 📝 Notas Importantes

- Os dados são **mockados** (não são reais)
- Perfeito para **demonstração e apresentação**
- Pronto para conectar com APIs reais da B3
- Código limpo e bem estruturado
- Totalmente responsivo

## 🆘 Problemas Comuns

**Backend não inicia:**
```powershell
# Certifique-se de que o venv está ativado
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Frontend não conecta ao backend:**
- Verifique se o backend está rodando em http://localhost:8000
- Verifique o CORS no backend/main.py

**Erro de pacotes:**
```powershell
cd frontend
npm install
```

---

**MVP Pronto! 🎉 Apresente com orgulho aos sócios!**

