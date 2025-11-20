from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .config import settings


class FeatureStore:
    """
    Persistência simples nos formatos bronze/silver/gold.
    Bronze = JSON bruto, Silver = DataFrame com features agregadas.
    """

    def __init__(self) -> None:
        self.settings = settings

    def save_bronze(self, symbol: str, payload: Dict[str, Any]) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        path = self.settings.bronze_dir / f"{symbol}_{timestamp}.json"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        return path

    def save_silver(self, symbol: str, rows: List[Dict[str, Any]]) -> Path:
        if not rows:
            raise ValueError(f"Nenhum dado calculado para {symbol}")

        df = pd.DataFrame(rows)
        df = df.sort_values("date")

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        path = self.settings.silver_dir / f"{symbol}_{timestamp}.parquet"
        df.to_parquet(path, index=False)
        return path

    def load_silver_dataset(self) -> pd.DataFrame:
        files = sorted(self.settings.silver_dir.glob("*.parquet"))
        if not files:
            raise FileNotFoundError("Nenhum dataset silver encontrado. Rode primeiro python ingest.py")

        frames = [pd.read_parquet(file) for file in files]
        return pd.concat(frames, ignore_index=True)


def bundle_to_feature_rows(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Converte o bundle vindo da Tradebox em linhas utilizáveis para modelos.
    Cada linha corresponde a um ponto diário com features calculadas.
    """
    symbol = bundle.get("symbol")
    history = (bundle.get("histories") or {}).get("data") or []
    fundamentals = (bundle.get("fundamentals") or {}).get("data") or [{}]
    fundamentals_flat = fundamentals[0] if fundamentals else {}

    rows: List[Dict[str, Any]] = []

    closes = []
    volumes = []

    for item in history:
        close = float(item.get("close") or item.get("price_close") or 0)
        volume = float(item.get("volume") or 0)
        closes.append(close)
        volumes.append(volume)
        date = item.get("price_date") or item.get("date")

        row: Dict[str, Any] = {
            "symbol": symbol,
            "date": date,
            "close": close,
            "open": float(item.get("open") or close),
            "high": float(item.get("high") or close),
            "low": float(item.get("low") or close),
            "volume": volume,
        }

        rows.append(row)

    if not rows:
        return rows

    df = pd.DataFrame(rows).sort_values("date")
    df["close_ma_5"] = df["close"].rolling(window=5, min_periods=1).mean()
    df["close_ma_20"] = df["close"].rolling(window=20, min_periods=1).mean()
    df["close_std_20"] = df["close"].rolling(window=20, min_periods=1).std().fillna(0)
    df["daily_return"] = df["close"].pct_change().fillna(0)
    df["volume_ma_20"] = df["volume"].rolling(window=20, min_periods=1).mean()

    # Copiar indicadores fundamentalistas para cada linha (broadcast)
    for key, value in fundamentals_flat.items():
        if isinstance(value, str):
            value = value.replace(".", "").replace(",", ".") if value.replace(".", "", 1).isdigit() else value
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue
        df[f"fund_{key}"] = numeric_value

    return df.to_dict(orient="records")
