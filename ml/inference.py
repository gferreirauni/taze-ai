from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd

from .config import settings
from .feature_store import FeatureStore

MODEL_PATH = Path("ml/models/buyhold_xgb.pkl")
MIN_RET = -0.15
MAX_RET = 0.15
RISK_LOW = 0.015
RISK_HIGH = 0.035

STATUS_RULES = [
    ("NEUTRO", "🔴", 0.0, 5.0, "Sem gatilhos relevantes. Continue monitorando."),
    ("RADAR", "🟡", 5.0, 6.0, "Ativo em aquecimento. Volume em linha e score crescente."),
    ("COMPRA", "🟢", 6.0, 10.0, "Score alto. Avalie entrada conforme seu perfil."),
]


def prediction_to_score(prediction: float, risk_value: float) -> float:
    clamped = max(MIN_RET, min(MAX_RET, prediction))
    normalized = (clamped - MIN_RET) / (MAX_RET - MIN_RET)
    base_score = normalized * 10

    if risk_value < RISK_LOW:
        penalty = 0.0
    elif risk_value < RISK_HIGH:
        penalty = 0.4
    else:
        penalty = 0.8

    return float(np.clip(base_score - penalty, 0.0, 10.0))


def load_model() -> Tuple[object, List[str]]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Modelo não encontrado. Execute `python -m ml.train_buyhold` primeiro.")
    bundle = joblib.load(MODEL_PATH)
    if isinstance(bundle, dict) and "model" in bundle:
        model = bundle["model"]
        feature_names = bundle.get("feature_names") or getattr(model, "feature_names_in_", [])
        return model, list(feature_names)
    return bundle, list(getattr(bundle, "feature_names_in_", []))


def score_to_status(score: float) -> Dict[str, str]:
    for name, emoji, lower, upper, msg in STATUS_RULES:
        if lower <= score < upper:
            return {"status": name, "emoji": emoji, "message": msg}
    return {"status": "NEUTRO", "emoji": "🔴", "message": "Sem gatilhos relevantes."}


def analyze_market(symbols: List[str]) -> List[Dict[str, object]]:
    model, feature_names = load_model()
    store = FeatureStore()
    df = store.load_silver_dataset()
    df["date"] = pd.to_datetime(df["date"])

    results: List[Dict[str, object]] = []

    for symbol in symbols:
        subset = df[df["symbol"] == symbol]
        if subset.empty:
            continue

        latest = subset.sort_values("date").iloc[-1]
        for col in feature_names:
            if col not in latest.index:
                latest[col] = 0.0

        features = latest[feature_names].astype(float).fillna(0.0).values.reshape(1, -1)
        raw_pred = float(model.predict(features)[0])
        risk = float(latest.get("volatility_30") or latest.get("volatility_21") or 0.02)
        score = prediction_to_score(raw_pred, risk)

        status_info = score_to_status(score)

        results.append(
            {
                "symbol": symbol,
                "current_price": float(latest.get("close", 0.0)),
                "score": round(score, 1),
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
