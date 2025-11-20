from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .config import settings

FUNDAMENTAL_FIELDS = {
    "indicators_pl": "fund_pl",
    "indicators_div_yield": "fund_dividend_yield",
    "indicators_roe": "fund_roe",
    "indicators_pvp": "fund_pvp",
    "indicators_net_margin": "fund_net_margin",
    "indicators_lpa": "fund_lpa",
    "indicators_vpa": "fund_vpa",
    "market_value": "fund_market_cap",
    "oscillations_12_months": "fund_osc_12m",
}


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("%", "").replace("R$", "").strip()
        cleaned = cleaned.replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


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

        df = pd.DataFrame(rows).sort_values("date")

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
    Converte o bundle vindo da Tradebox em linhas utilizáveis com indicadores técnicos avançados.
    """
    symbol = bundle.get("symbol")
    history = (bundle.get("histories") or {}).get("data") or []
    fundamentals = (bundle.get("fundamentals") or {}).get("data") or [{}]
    fundamentals_flat = fundamentals[0] if fundamentals else {}

    if not history:
        return []

    rows: List[Dict[str, Any]] = []
    for item in history:
        close = float(item.get("close") or item.get("price_close") or 0)
        if close <= 0:
            continue
        rows.append(
            {
                "symbol": symbol,
                "date": item.get("price_date") or item.get("date"),
                "close": close,
                "open": float(item.get("open") or close),
                "high": float(item.get("high") or close),
                "low": float(item.get("low") or close),
                "volume": float(item.get("volume") or 0),
            }
        )

    df = pd.DataFrame(rows).sort_values("date")
    if df.empty:
        return []

    df["close_ma_20"] = df["close"].rolling(window=20).mean()
    df["close_ma_21"] = df["close"].rolling(window=21).mean()
    df["close_ma_50"] = df["close"].rolling(window=50).mean()
    df["close_ma_200"] = df["close"].rolling(window=200).mean()
    df["close_ma_200"] = df["close"].rolling(window=200).mean()

    df["close_ema_9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["close_ema_21"] = df["close"].ewm(span=21, adjust=False).mean()

    df["daily_return"] = df["close"].pct_change().fillna(0)
    df["volatility_21"] = df["daily_return"].rolling(window=21).std().fillna(0)
    df["volatility_30"] = df["daily_return"].rolling(window=30).std().fillna(0)
    df["volume_ma_20"] = df["volume"].rolling(window=20).mean()
    df["rsi_14"] = calculate_rsi(df["close"])

    exp12 = df["close"].ewm(span=12, adjust=False).mean()
    exp26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd_line"] = exp12 - exp26
    df["macd_signal"] = df["macd_line"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd_line"] - df["macd_signal"]

    bb_period = 20
    bb_std = 2
    df["bb_mid"] = df["close"].rolling(window=bb_period).mean()
    df["bb_std"] = df["close"].rolling(window=bb_period).std()
    df["bb_upper"] = df["bb_mid"] + (bb_std * df["bb_std"])
    df["bb_lower"] = df["bb_mid"] - (bb_std * df["bb_std"])
    df["bb_pband"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])

    df["momentum_10"] = df["close"].pct_change(periods=10).fillna(0)

    for source_key, target_key in FUNDAMENTAL_FIELDS.items():
        numeric_value = _safe_float(fundamentals_flat.get(source_key))
        if numeric_value is not None:
            df[target_key] = numeric_value

    df = df.dropna().fillna(0)

    return df.to_dict(orient="records")
