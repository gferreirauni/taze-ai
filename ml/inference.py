from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

import joblib
import numpy as np
import pandas as pd

from .config import settings
from .feature_store import FeatureStore

MODEL_PATH = Path("ml/models/buyhold_xgb.pkl")

FEATURE_COLUMNS = [
    "close",
    "volume",
    "close_ma_20",
    "close_ma_50",
    "close_ma_200",
    "daily_return",
    "volatility_21",
    "rsi_14",
    "macd_line",
    "macd_signal",
    "macd_hist",
    "bb_upper",
    "bb_lower",
    "bb_pband",
    "momentum_10",
]

STATUS_RULES = [
    ("NEUTRO", "🔴", 0.0, 5.0, "Sem gatilhos relevantes. Continue monitorando."),
    ("RADAR", "🟡", 5.0, 6.0, "Ativo em aquecimento. Volume em linha e score crescente."),
    ("COMPRA", "🟢", 6.0, 10.0, "Score alto. Avalie entrada conforme seu perfil."),
]


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Modelo não encontrado. Execute `python -m ml.train_buyhold` primeiro.")
    bundle = joblib.load(MODEL_PATH)
    if isinstance(bundle, dict) and "model" in bundle:
        return bundle["model"]
    return bundle


def score_to_status(score: float) -> Dict[str, str]:
    for name, emoji, lower, upper, msg in STATUS_RULES:
        if lower <= score < upper:
            return {
                "status": name,
                "emoji": emoji,
                "message": msg,
            }
    return {
        "status": "NEUTRO",
        "emoji": "🔴",
        "message": "Sem gatilhos relevantes.",
    }


def analyze_market(symbols: List[str]) -> List[Dict[str, object]]:
    model = load_model()
    store = FeatureStore()
    df = store.load_silver_dataset()
    df["date"] = pd.to_datetime(df["date"])

    results: List[Dict[str, object]] = []

    for symbol in symbols:
        subset = df[df["symbol"] == symbol]
        if subset.empty:
            continue

        latest = subset.sort_values("date").iloc[-1]
        features = latest[FEATURE_COLUMNS].astype(float).fillna(0.0).values.reshape(1, -1)
        score = float(np.clip(model.predict(features)[0], 0, 10))

        status_info = score_to_status(score)

        results.append(
            {
                "symbol": symbol,
                "current_price": float(latest["close"]),
                "score": round(score, 2),
                "status": status_info["status"],
                "status_emoji": status_info["emoji"],
                "msg": status_info["message"],
                "last_update": latest["date"].strftime("%Y-%m-%d"),
            }
        )

    return results


if __name__ == "__main__":
    data = analyze_market(settings.tickers)
    print(json.dumps(data, indent=2, ensure_ascii=False))
