from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple

import joblib
import numpy as np
import pandas as pd

from .feature_store import FeatureStore

try:
    from xgboost import XGBRegressor
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "xgboost não está instalado. Rode `pip install -r ml/requirements.txt` antes de treinar."
    ) from exc


def engineer_targets(df: pd.DataFrame, horizon_days: int = 90) -> Tuple[pd.DataFrame, np.ndarray]:
    """Cria a variável alvo (retorno acumulado no horizonte)."""
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    df["future_price"] = df.groupby("symbol")["close"].shift(-horizon_days)
    df["target_return"] = (df["future_price"] - df["close"]) / df["close"]
    df = df.dropna(subset=["target_return"])
    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    feature_cols = [
        "close",
        "close_ma_5",
        "close_ma_20",
        "close_std_20",
        "daily_return",
        "volume",
        "volume_ma_20",
        "volatility_30",
        "rsi_14",
    ]
    feature_cols += [col for col in df.columns if col.startswith("fund_")]

    X = df[feature_cols].fillna(0)
    y = df["target_return"].values
    return X, y


def train_model(X: pd.DataFrame, y: np.ndarray) -> XGBRegressor:
    model = XGBRegressor(
        n_estimators=600,
        max_depth=4,
        learning_rate=0.03,
        subsample=0.75,
        colsample_bytree=0.75,
        objective="reg:squarederror",
        n_jobs=4,
    )
    model.fit(X, y)
    return model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Treino do modelo Buy & Hold (score Warren)")
    parser.add_argument("--output", default="models/buyhold_xgb.pkl", help="Onde salvar o modelo treinado")
    parser.add_argument("--horizon-days", type=int, default=90, help="Horizonte de previsão em dias")
    parser.add_argument(
        "--train-until",
        default="2022-12-31",
        help="Data limite (YYYY-MM-DD) para treino. Dados posteriores são ignorados.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    store = FeatureStore()
    df = store.load_silver_dataset()
    df["date"] = pd.to_datetime(df["date"])
    cutoff = pd.to_datetime(args.train_until)
    print(f"[TRAIN] Datas disponíveis: {df['date'].min()} → {df['date'].max()}")
    df = df[df["date"] <= cutoff].copy()
    if df.empty:
        raise SystemExit(f"Nenhum dado disponível até {args.train_until}. Rode ingest novamente ou ajuste o corte.")

    X, y = engineer_targets(df, horizon_days=args.horizon_days)
    print(f"[TRAIN] Dataset final: {X.shape[0]} linhas x {X.shape[1]} features")

    model = train_model(X, y)
    preds = model.predict(X)
    rmse = float(np.sqrt(np.mean((preds - y) ** 2)))
    print(f"[TRAIN] RMSE (in-sample): {rmse:.5f}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "rmse_in_sample": rmse,
            "horizon_days": args.horizon_days,
            "feature_count": X.shape[1],
            "train_until": cutoff.strftime("%Y-%m-%d"),
        },
        output_path,
    )
    print(f"[TRAIN] Modelo salvo em {output_path}")
