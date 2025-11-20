# Módulo de Machine Learning (Vidente)

Este diretório centraliza tudo o que pertence ao “Vidente”: ingestão dos dados históricos da Tradebox, transformação em features reutilizáveis e treinamento de modelos proprietários (ex.: score Warren com XGBoost). A ideia é manter o pipeline desacoplado do backend (`backend/`) para podermos iterar e escalar modelos sem tocar nas rotas de produção.

## Estrutura

```
ml/
├── README.md                  ← este arquivo
├── __init__.py
├── requirements.txt           ← libs específicas do pipeline (xgboost, prefect etc.)
├── config.py                  ← carregamento de variáveis de ambiente e diretórios
├── tradebox_client.py         ← cliente assíncrono para buscar lotes na Tradebox
├── feature_store.py           ← helpers para persistir bronze/silver/gold
├── ingest.py                  ← script que orquestra a ingestão + transformação
├── train_buyhold.py           ← primeiro modelo proprietário (score Buy & Hold)
└── data/
    ├── bronze/                ← dumps crus (JSON/Parquet) “como veio” da Tradebox
    ├── silver/                ← dados limpos + features agregadas
    └── gold/                  ← sinais já prontos para o backend consumir
```

## Variáveis de ambiente

O módulo reutiliza o `.env` da raiz. Garanta que os valores abaixo existam antes de rodar qualquer script:

```
TRADEBOX_API_USER=TradeBox
TRADEBOX_API_PASS=TradeBoxAI@2025
TRADEBOX_BASE_URL=https://api.tradebox.com.br/v1
```

Valores opcionais (podem ser sobrescritos via env):

```
ML_TICKERS=PETR4,BBAS3,VALE3,MGLU3,WEGE3
ML_HISTORY_RANGE=365      # em dias
ML_OUTPUT_DIR=ml/data
```

## Fluxo rápido

1. Instale as dependências específicas:
   ```bash
   cd ml
   pip install -r requirements.txt
   ```
2. Rode a ingestão para gerar os datasets bronze/silver:
   ```bash
   python ingest.py --range-days 365 --tickers PETR4 BBAS3 VALE3
   ```
3. Treine o primeiro modelo proprietário (score Warren / Buy & Hold):
   ```bash
   python train_buyhold.py --input silver --output models/buyhold.pkl
   ```
4. (Opcional) Agende o `ingest.py` em um orquestrador (Prefect/Airflow) para rodar diariamente, e `train_buyhold.py` semanalmente/mensalmente.

## Próximos passos sugeridos

- Implementar `generate_signals.py` para publicar previsões noturnas no Redis/Postgres usado pelo backend.
- Adicionar rastreamento (MLflow ou JSON) para versionar modelos/metrics.
- Criar notebooks de avaliação usando os datasets `silver/` e `gold/`.
