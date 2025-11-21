from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd

from .config import settings
from .feature_store import FeatureStore
from .db_client import save_signals

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


def load_latest_bundle(symbol: str, store: FeatureStore) -> Dict[str, Any] | None:
    files = sorted(store.settings.bronze_dir.glob(f"{symbol}_*.json"))
    if not files:
        return None
    return json.loads(files[-1].read_text(encoding="utf-8"))


def extract_stock_metadata(bundle: Dict[str, Any] | None) -> Dict[str, Any] | None:
    if not bundle:
        return None
    info_rows = (bundle.get("info") or {}).get("data") or []
    if not info_rows:
        return None
    info = info_rows[0]
    return {
        "name": info.get("company"),
        "sector": info.get("sector"),
        "segment": info.get("segment"),
        "document_number": info.get("document_number"),
        "homepage": info.get("homepage"),
        "logo": info.get("company_picture"),
    }


def extract_intraday(bundle: Dict[str, Any] | None) -> Tuple[Dict[str, Any] | None, List[Dict[str, Any]] | None]:
    if not bundle:
        return None, None
    intraday_rows = (bundle.get("intraday") or {}).get("data") or []
    if not intraday_rows:
        return None, None

    sorted_rows = sorted(intraday_rows, key=lambda row: row.get("price_date") or "", reverse=True)
    latest = sorted_rows[0]

    def _float(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    latest_price = _float(latest.get("price") or latest.get("close") or latest.get("open"))
    latest_open = _float(latest.get("open"))
    change_value = None
    if latest_price is not None:
        base = latest_open if latest_open is not None else latest_price
        change_value = latest_price - base

    snapshot = {
        "price": latest_price,
        "open": latest_open,
        "close": _float(latest.get("close")) if latest.get("close") is not None else latest_price,
        "high": _float(latest.get("high")),
        "low": _float(latest.get("low")),
        "volume": _float(latest.get("volume")),
        "percent": _float(latest.get("percent")),
        "change": change_value,
        "timestamp": latest.get("price_date"),
    }

    series = []
    for row in reversed(sorted_rows[:60]):
        price = _float(row.get("price") or row.get("close"))
        if price is None:
            continue
        series.append({"time": row.get("price_date"), "price": price})

    return snapshot, series or None


def extract_fundamentals(bundle: Dict[str, Any] | None) -> Dict[str, Any] | None:
    if not bundle:
        return None
    fundamentals_rows = (bundle.get("fundamentals") or {}).get("data") or []
    if not fundamentals_rows:
        return None
    return fundamentals_rows[0]


def _format_float(value: Any, suffix: str = "") -> str | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return f"{number:.1f}{suffix}"


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
        rsi_value = float(latest.get("rsi_14")) if pd.notna(latest.get("rsi_14")) else None
        score = prediction_to_score(raw_pred, risk)

        status_info = score_to_status(score)
        analysis_dt = pd.Timestamp(latest["date"]).to_pydatetime()

        bundle = load_latest_bundle(symbol, store)
        stock_metadata = extract_stock_metadata(bundle)
        intraday_snapshot, intraday_series = extract_intraday(bundle)
        fundamentals_payload = extract_fundamentals(bundle)

        current_price = (
            float(intraday_snapshot.get("price"))
            if intraday_snapshot and intraday_snapshot.get("price") is not None
            else float(latest.get("close", 0.0))
        )

        fundamentals_blurbs: List[str] = []
        if fundamentals_payload:
            pl = _format_float(fundamentals_payload.get("indicators_pl"))
            dy = _format_float(fundamentals_payload.get("indicators_div_yield"), "%")
            osc = _format_float(fundamentals_payload.get("oscillations_12_months"), "%")
            if pl:
                fundamentals_blurbs.append(f"P/L {pl}")
            if dy:
                fundamentals_blurbs.append(f"DY {dy}")
            if osc:
                fundamentals_blurbs.append(f"12m {osc}")

        ai_analysis = status_info["message"]
        if fundamentals_blurbs:
            ai_analysis = f"{ai_analysis} ({' | '.join(fundamentals_blurbs)})"

        results.append(
            {
                "symbol": symbol,
                "current_price": current_price,
                "score": round(score, 1),
                "status": status_info["status"],
                "status_emoji": status_info["emoji"],
                "msg": status_info["message"],
                "ai_analysis": ai_analysis,
                "last_update": analysis_dt.strftime("%Y-%m-%d"),
                "analysis_date": analysis_dt.isoformat(),
                "rsi": rsi_value,
                "volatility": risk,
                "stock_metadata": stock_metadata,
                "intraday": intraday_snapshot,
                "intraday_series": intraday_series,
                "fundamentals": fundamentals_payload,
            }
        )

    return results


if __name__ == "__main__":
    data = analyze_market(settings.tickers)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    save_signals(data)
