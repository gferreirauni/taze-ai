# Taze AI – Plataforma Inteligente de Investimentos para B3

![Version](https://img.shields.io/badge/version-2.4.0-emerald)
![Python](https://img.shields.io/badge/python-3.13-blue)
![Next.js](https://img.shields.io/badge/next.js-15-black)
![License](https://img.shields.io/badge/license-MIT-green)

Taze AI é um painel SaaS de inteligência para investidores brasileiros que combina dados profissionais da Tradebox, modelos proprietários e o GPT‑4o para entregar decisões prontas (COMPRA/MANTER/VENDA) em segundos.

---

## Visão Geral

| Pilar | Descrição |
|-------|-----------|
| **Painel de Decisão** | Carrosséis com análise Warren/Trader/Viper, geração inline e indicadores visuais (0‑10). |
| **Chat Assistant** | GPT‑4o com Function Calling para responder perguntas sobre PETR4, VALE3 etc. |
| **Vidente (ML Proprietário)** | Pipeline em `ml/` que treina XGBoost com 27 anos de fundamentos + técnicos, gera o **Score Taze ML** e alimenta o frontend. |
| **Backtesting & Alpha** | Script `ml/backtest.py` simula a carteira Taze versus Buy & Hold e produz gráficos/relatórios. |
| **Observabilidade e Cache** | Cache multi‑camada (Redis opcional) para ações, análises e notícias; requisições paralelas com asyncio. |

---

## Funcionalidades Principais

### 1. Painel de IA com 3 Perfis
- **Warren (Buy & Hold)** – análise fundamentalista + Score Taze ML (badge “Baseado em 27 anos de histórico”).
- **Trader (Swing Trade)** – análise técnica (médias, suportes, tendência).
- **Viper (Day Trade)** – leitura de volatilidade, oscillations_day e range diário.
- Recomendações claras: `COMPRA FORTE`, `COMPRA`, `MANTER`, `VENDA`.

### 2. Chat Inteligente
- Prompt especializado em B3, responde em PT‑BR.
- Function Calling: quando o usuário cita “VALE3”, a IA busca dados atualizados antes de responder.
- Encadeamento com o Painel (mesma fonte de dados e Score ML disponíveis via contexto).

### 3. Feed de Notícias
- Scraping do portal Análise de Ações com fallback seguro.
- Carrossel vertical autônomo, atualização a cada 15 minutos.

### 4. Inteligência Proprietária (“O Vidente”)
- `ml/ingest.py`: baixa histórico completo, calcula features (RSI, volatilidade, médias, fundamentos).
- `ml/train_buyhold.py`: treina XGBoost (score Buy & Hold), salva `ml/models/buyhold_xgb.pkl`.
- `ml/inference.py`: serviço carregado pelo backend que gera `predictiveSignals` (score 0‑10, risco BAIXO/MODERADO/ALTO).
- Backend injeta `predictiveSignals` após cada chamada à Tradebox e repassa ao GPT e ao frontend.

### 5. Backtesting de Valor
- `ml/backtest.py`: simula 2 carteiras (Taze AI vs Buy & Hold) nos últimos 24 meses usando os dados `silver/`.
- Critérios: abre posição se Score > 7, zera se Score < 4, começa com R$ 10.000.
- Output inclui resultados por ativo + Alpha (%) e, se Matplotlib estiver instalado, gráficos em `ml/results/`.

---

## Arquitetura

```
frontend/ (Next.js 15, React 19, Tailwind)
│
├── app/ (App Router, páginas e API routes)
├── components/dashboard/AIScoreCard.tsx  ← destaque para Score Taze ML
└── ... 

backend/ (FastAPI + GPT-4o + Tradebox)
│
├── main.py
│   ├── /api/stocks            ← agrega info intraday + fundamentals + predictiveSignals
│   ├── /api/ai/analyze        ← GPT-4o + Score Taze no prompt
│   ├── /api/ai/chat           ← assistente com Function Calling
│   └── /api/news              ← scraping com cache
└── cache_manager.py           ← Redis opcional + fallback em memória

ml/
├── config.py / tradebox_client.py / feature_store.py
├── ingest.py                  ← pipeline bronze → silver
├── train_buyhold.py           ← treino XGBoost (Score Warren)
├── inference.py               ← PredictiveService usado pelo backend
├── backtest.py                ← carteiras Taze x Buy & Hold
└── data/bronze|silver|gold    ← datasets persistidos
```

---

## Tecnologias

| Camada | Tecnologias |
|--------|-------------|
| Backend | FastAPI · httpx · Pydantic · OpenAI GPT‑4o · Redis opcional |
| Frontend | Next.js 15 (App Router) · React 19 · TypeScript · Tailwind · Embla Carousel · Lucide Icons |
| ML / Pipelines | Python 3.13 · pandas · numpy · xgboost · pyarrow · scikit-learn · matplotlib (opcional) |
| Dados | Tradebox API (intraday, histories, fundamentals) · Brapi (backup) |

---

## Setup e Execução

### 1. Clonar e configurar
```bash
git clone https://github.com/seu-usuario/tazeai.git
cd tazeai
```

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

cp .env.example .env  # ou crie manualmente
python main.py
```

`.env` esperado (exemplo):
```
OPENAI_API_KEY=sk-proj-xxxx
TRADEBOX_API_USER=TradeBox
TRADEBOX_API_PASS=TradeBoxAI@2025
BRAPI_TOKEN=seu_token
REDIS_URL=redis://localhost:6379/0  # opcional
```

### 3. Frontend
```bash
cd ../frontend
npm install
npm run dev
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### 4. Pipeline do Vidente
```bash
cd ../
pip install -r ml/requirements.txt

# Ingestão (27 anos ≈ 10.000 dias; ticker a ticker com ML_CONCURRENCY=1)
ML_CONCURRENCY=1 python -m ml.ingest --range-days 10000

# Treino do modelo
python -m ml.train_buyhold
```
O arquivo `ml/models/buyhold_xgb.pkl` será criado/atualizado e o backend já utilizará o novo score.

### 5. Backtesting (opcional)
```bash
python ml/backtest.py
```
Saída esperada:
```
[PETR4] Resultado Taze AI: R$ 14.500 (+45.00%)
[PETR4] Resultado Buy&Hold: R$ 12.000 (+20.00%)
[PETR4] Alpha (Diferença): +25.00% 🏆
...
[BACKTEST] Alpha médio na carteira monitorada: +18.42%
```
Se `matplotlib` estiver instalado, gráficos serão salvos em `ml/results/`.

---

## Como o Score Taze ML é usado
1. `ml/ingest.py` gera datasets **silver** com features técnicas + 50 indicadores fundamentalistas (ex.: P/L, DY, ROE, Margem Líquida).
2. `ml/train_buyhold.py` treina o XGBoost e armazena metadata (features, RMSE, horizonte).
3. `backend/main.py` instância `PredictiveService`, que:
   - Calcula RSI/volatilidade com os dados em cache.
   - Prediz retorno, converte para score 0‑10, aplica penalização por risco.
   - Injeta `predictiveSignals` em `/api/stocks`.
4. O endpoint `/api/ai/analyze` inclui esses sinais no prompt do GPT-4o (bloco `[DADOS INTERNOS TAZE AI]`) e o frontend exibe o card “Score Taze ML”.

---

## Endpoints Principais

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET`  | `/api/stocks` | Lista as ações monitoradas (dados Tradebox + `predictiveSignals`). |
| `GET`  | `/api/stocks/{symbol}` | Detalhes pontuais (backup Brapi). |
| `POST` | `/api/ai/analyze` | Aciona o GPT‑4o para gerar a análise Warren/Trader/Viper. |
| `GET`  | `/api/ai/analysis/{symbol}` | Retorna a análise em cache (24h). |
| `POST` | `/api/ai/chat` | Chat financeiro com Function Calling. |
| `GET`  | `/api/news` | Feed de notícias via scraping com fallback. |

---

## Cache & Performance

- **CacheManager**: Redis (se disponível) ou memória local com TTL configurável (ações 5 min, análises 24h, notícias 15 min).
- **AsyncIO + httpx**: requisições simultâneas para `assetInformation`, `assetIntraday`, `assetHistories`, `assetFundamentals`.
- **Histórico otimizado**: Tradebox com `?range=3mo` e fallback `slice(-90)` se necessário.
- **Backpressure**: ao enriquecer com `predictiveSignals`, o cache é sempre atualizado e reduz chamadas redundantes ao modelo.

---

## Próximos Passos

- Autenticação + carteira personalizada por usuário.
- Alertas proativos via e‑mail/push (com base no Score Taze + variação intraday).
- Integração com corretoras e importação de notas.
- Expansão para FIIs e top 20 da B3.
- App mobile (React Native) espelhando o Painel de Decisão.

---

## Contribuições

1. Faça fork.
2. Crie uma branch: `git checkout -b feature/minha-feature`.
3. Commit: `git commit -m "feat: adiciona XYZ"`.
4. Push: `git push origin feature/minha-feature`.
5. Abra um Pull Request.

---

## Licença

Projeto licenciado sob MIT. Leia [LICENSE](LICENSE) para mais detalhes.

---

## Suporte

- Abra uma issue neste repositório para dúvidas ou bugs.
- Ideias de melhoria? Vamos conversar no PR!

**Taze AI** – “Nossos modelos matemáticos indicam o próximo movimento.” 🔮📈
