from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Mapping, Any, Sequence

import psycopg2
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL não encontrado. Configure-o no arquivo .env.")
    return psycopg2.connect(database_url)


def ensure_stock(cursor, symbol: str) -> None:
    cursor.execute(
        'INSERT INTO "Stock" (symbol) VALUES (%s) ON CONFLICT (symbol) DO NOTHING',
        (symbol,),
    )


def parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
    return datetime.utcnow()


def _get_float(record: Mapping[str, Any], key: str) -> float | None:
    value = record.get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def save_signals(signals_data: Sequence[Mapping[str, Any]]) -> None:
    if not signals_data:
        print("[DB] Nenhum sinal para persistir.")
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            for signal in signals_data:
                symbol = signal.get("symbol")
                if not symbol:
                    continue

                ensure_stock(cur, symbol)

                analysis_date = parse_datetime(signal.get("last_update"))
                price = _get_float(signal, "current_price") or 0.0
                score = _get_float(signal, "score") or 0.0
                status = signal.get("status") or "NEUTRO"
                rsi = _get_float(signal, "rsi")
                volatility = _get_float(signal, "volatility")
                ai_analysis = signal.get("msg")

                cur.execute(
                    '''
                    INSERT INTO "Signal" (
                        "stockSymbol",
                        price,
                        score,
                        status,
                        rsi,
                        volatility,
                        "aiAnalysis",
                        "analysisDate"
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''',
                    (symbol, price, score, status, rsi, volatility, ai_analysis, analysis_date),
                )

        conn.commit()
    print("✅ Sinais salvos no Banco de Dados PostgreSQL.")
