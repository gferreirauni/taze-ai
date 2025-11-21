from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
import time
from typing import List

from .config import settings
from .feature_store import FeatureStore, bundle_to_feature_rows
from .tradebox_client import TradeboxClient


async def ingest_symbol(symbol: str, client: TradeboxClient, store: FeatureStore, range_days: int) -> None:
    bundle = await client.fetch_asset_bundle(symbol, range_days=range_days)
    store.save_bronze(symbol, bundle)

    rows = bundle_to_feature_rows(bundle)
    if not rows:
        print(f"[WARN] Nenhum histórico retornado para {symbol}")
        return

    path = store.save_silver(symbol, rows)
    print(f"[OK] {symbol}: {len(rows)} linhas -> {path}")


async def run_pipeline(tickers: List[str], range_days: int) -> None:
    client = TradeboxClient()
    store = FeatureStore()

    for ticker in tickers:
        await ingest_symbol(ticker, client, store, range_days)
        print("⏳ Aguardando 2 segundos para não sobrecarregar a API...")
        time.sleep(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingestão de dados Tradebox -> Feature Store")
    parser.add_argument("--tickers", nargs="*", default=settings.tickers, help="Lista de ativos (default = ML_TICKERS)")
    parser.add_argument(
        "--range-days",
        type=int,
        default=settings.history_range_days,
        help="Janela de histórico em dias",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    started = datetime.now()
    print(f"[INGEST] Iniciando pipeline - tickers={args.tickers} range={args.range_days}d")
    asyncio.run(run_pipeline(args.tickers, args.range_days))
    elapsed = (datetime.now() - started).total_seconds()
    print(f"[INGEST] Finalizado em {elapsed:.2f}s -> dados em {settings.data_root}")
