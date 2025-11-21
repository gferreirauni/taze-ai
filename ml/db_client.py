from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse, parse_qs

import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL não encontrado. Configure-o no arquivo .env.")

    parsed = urlparse(database_url)
    query = parse_qs(parsed.query)
    schema = (query.get("schema") or [None])[0]

    conn_kwargs = {
        "dbname": parsed.path.lstrip("/") or None,
        "user": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname or "127.0.0.1",
        "port": parsed.port or 5432,
    }
    if schema:
        conn_kwargs["options"] = f"-c search_path={schema}"

    return psycopg2.connect(**conn_kwargs)


def upsert_stock(cursor, symbol: str, metadata: Mapping[str, Any] | None = None) -> None:
    if not metadata:
        cursor.execute(
            'INSERT INTO "Stock" (symbol) VALUES (%s) ON CONFLICT (symbol) DO NOTHING',
            (symbol,),
        )
        return

    cursor.execute(
        '''
        INSERT INTO "Stock" (symbol, name, sector, segment, "documentNumber", homepage, "logoUrl")
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol) DO UPDATE SET
            name = COALESCE(EXCLUDED.name, "Stock".name),
            sector = COALESCE(EXCLUDED.sector, "Stock".sector),
            segment = COALESCE(EXCLUDED.segment, "Stock".segment),
            "documentNumber" = COALESCE(EXCLUDED."documentNumber", "Stock"."documentNumber"),
            homepage = COALESCE(EXCLUDED.homepage, "Stock".homepage),
            "logoUrl" = COALESCE(EXCLUDED."logoUrl", "Stock"."logoUrl")
        ''',
        (
            symbol,
            metadata.get("name"),
            metadata.get("sector"),
            metadata.get("segment"),
            metadata.get("document_number"),
            metadata.get("homepage"),
            metadata.get("logo"),
        ),
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
    if record is None:
        return None
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

                stock_metadata = signal.get("stock_metadata")
                upsert_stock(cur, symbol, stock_metadata)

                analysis_date = parse_datetime(signal.get("analysis_date") or signal.get("last_update"))
                price = _get_float(signal, "current_price") or 0.0
                score = _get_float(signal, "score") or 0.0
                status = signal.get("status") or "NEUTRO"
                rsi = _get_float(signal, "rsi")
                volatility = _get_float(signal, "volatility")
                ai_analysis = signal.get("ai_analysis") or signal.get("msg")

                intraday = signal.get("intraday") or {}
                intraday_open = _get_float(intraday, "open")
                intraday_close = _get_float(intraday, "close") or price
                intraday_high = _get_float(intraday, "high")
                intraday_low = _get_float(intraday, "low")
                intraday_volume = _get_float(intraday, "volume")
                intraday_change = _get_float(intraday, "change")
                intraday_percent = _get_float(intraday, "percent")
                intraday_series = signal.get("intraday_series")
                fundamentals = signal.get("fundamentals")

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
                        "intradayOpen",
                        "intradayClose",
                        "intradayHigh",
                        "intradayLow",
                        "intradayVolume",
                        "intradayChange",
                        "intradayPercent",
                        "intradaySeries",
                        fundamentals,
                        "analysisDate"
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''',
                    (
                        symbol,
                        price,
                        score,
                        status,
                        rsi,
                        volatility,
                        ai_analysis,
                        intraday_open,
                        intraday_close,
                        intraday_high,
                        intraday_low,
                        intraday_volume,
                        intraday_change,
                        intraday_percent,
                        Json(intraday_series) if intraday_series else None,
                        Json(fundamentals) if fundamentals else None,
                        analysis_date,
                    ),
                )

        conn.commit()
    print("✅ Sinais salvos no Banco de Dados PostgreSQL.")
