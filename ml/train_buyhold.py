from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple, List

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor

# Importação relativa segura para execução como módulo
try:
    from .feature_store import FeatureStore
except ImportError:
    from ml.feature_store import FeatureStore

def engineer_targets(df: pd.DataFrame, horizon_days: int = 90) -> Tuple[pd.DataFrame, np.ndarray, List[str], pd.Series]:
    """
    Cria a variável alvo (retorno futuro) e prepara as features.
    Retorna: X (features), y (targets), feature_names, dates
    """
    # 1. Garantir que a data seja datetime
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    
    # 2. Ordenar para garantir shift correto
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    
    # 3. Criar Target (Retorno daqui a N dias)
    # shift(-N) pega o valor do futuro e traz para a linha atual
    df["future_price"] = df.groupby("symbol")["close"].shift(-horizon_days)
    df["target_return"] = (df["future_price"] - df["close"]) / df["close"]
    
    # 4. Limpeza: Removemos apenas as linhas que não têm futuro (os últimos 90 dias do dataset total)
    # Isso é feito ANTES de filtrar por data de treino, para aproveitar o máximo de dados.
    df = df.dropna(subset=["target_return"])
    
    # 5. Seleção de Features (Técnicas + Fundamentos)
    # Definimos as colunas técnicas padrão que sabemos que existem ou foram calculadas
    technical_cols = [
        "close_ma_20", "close_ma_50", "close_ma_200", # Médias Longas
        "rsi_14", "macd_hist", "bollinger_pband",     # Osciladores
        "volatility_30", "momentum_10",               # Risco/Tendência
        "volume_ma_20"
    ]
    
    # Pegamos dinamicamente todas as colunas de fundamentos (começam com fund_)
    fundamental_cols = [c for c in df.columns if c.startswith("fund_")]
    
    # Combinamos e filtramos apenas as que existem no DataFrame atual
    feature_cols = [c for c in (technical_cols + fundamental_cols) if c in df.columns]
    
    # 6. Preencher NaNs nas features (ex: médias móveis no início da série) com 0 ou ffill
    df_model = df.dropna(subset=feature_cols) # Opção segura: remover dias sem indicadores calculados
    
    X = df_model[feature_cols]
    y = df_model["target_return"].values
    dates = df_model["date"]
    
    return X, y, feature_cols, dates

def train_model(X: pd.DataFrame, y: np.ndarray) -> XGBRegressor:
    model = XGBRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        n_jobs=-1,
        random_state=42
    )
    model.fit(X, y)
    return model

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Treino do modelo Buy & Hold (score Warren)")
    parser.add_argument("--output", default="ml/models/buyhold_xgb.pkl", help="Caminho do modelo")
    parser.add_argument("--horizon-days", type=int, default=90, help="Horizonte de previsão")
    parser.add_argument("--train-until", default="2022-12-31", help="Data limite para treino (Split temporal)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    store = FeatureStore()
    
    print("[TRAIN] Carregando dados da Feature Store (Silver)...")
    try:
        df = store.load_silver_dataset()
    except FileNotFoundError:
        print("❌ Erro: Nenhum dado encontrado. Rode 'python -m ml.ingest --range-days 10000' primeiro.")
        exit(1)

    # Engenharia de Features no dataset completo
    X_all, y_all, features, dates_all = engineer_targets(df, horizon_days=args.horizon_days)
    
    # Conversão da data de corte
    cutoff_date = pd.to_datetime(args.train_until)
    
    print(f"[TRAIN] Período total disponível: {dates_all.min().date()} até {dates_all.max().date()}")
    print(f"[TRAIN] Filtrando treino até: {cutoff_date.date()}")

    # Filtro Temporal Rígido
    mask_train = dates_all < cutoff_date
    X_train = X_all[mask_train]
    y_train = y_all[mask_train]
    
    print(f"[TRAIN] Linhas de Treino: {len(X_train)} (de {len(X_all)} totais)")
    
    if len(X_train) == 0:
        print("❌ ERRO CRÍTICO: Dataset de treino vazio! Verifique se os dados históricos (Silver) contêm datas anteriores a 2023.")
        exit(1)

    # Treinamento
    print(f"[TRAIN] Treinando XGBoost com {len(features)} features...")
    model = train_model(X_train, y_train)
    
    # Métricas In-Sample
    preds = model.predict(X_train)
    rmse = float(np.sqrt(np.mean((preds - y_train) ** 2)))
    print(f"[TRAIN] RMSE (erro médio): {rmse:.5f}")

    # RAIO-X DO MODELO (Feature Importance)
    print("\n" + "="*40)
    print("   🔬 RAIO-X DO VIDENTE (Top 10 Fatores)")
    print("="*40)
    
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    for i in range(min(10, len(features))):
        idx = indices[i]
        print(f"{i+1:2d}. {features[idx]:<20} : {importances[idx]:.4f}")
    print("="*40 + "\n")

    # Salvar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "model": model,
        "feature_names": features,
        "rmse": rmse,
        "horizon_days": args.horizon_days,
        "train_until": args.train_until
    }, output_path)
    print(f"[TRAIN] ✅ Modelo salvo em: {output_path}")