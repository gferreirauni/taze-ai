from __future__ import annotations

from typing import Any, Dict
import asyncio

import httpx

from .config import settings


class TradeboxClient:
    """
    Cliente assíncrono simples para buscar blocos de dados diretamente da Tradebox.
    Reutiliza autenticação Basic Auth e permite adicionar novos endpoints facilmente.
    """

    def __init__(self) -> None:
        self._auth = httpx.BasicAuth(settings.tradebox_user, settings.tradebox_pass)
        self._base_url = settings.tradebox_base_url.rstrip("/")
        self._timeout = httpx.Timeout(30.0)

    async def fetch_asset_bundle(self, symbol: str, range_days: int | None = None) -> Dict[str, Any]:
        """
        Busca informações, históricos e fundamentals em paralelo.

        Args:
            symbol: código do ativo (ex.: PETR4)
            range_days: janela histórica em dias (default = settings.history_range_days)
        """
        symbol = symbol.upper()
        range_days = range_days or settings.history_range_days
        # Tradebox aceita range no formato "1y", "6mo" ou datas absolutas.
        # Converter range em meses aproximados para requests atuais.
        months = max(1, int(range_days / 30))
        range_param = f"{months}mo"

        urls = {
            "info": f"{self._base_url}/assetInformation/{symbol}",
            "intraday": f"{self._base_url}/assetIntraday/{symbol}",
            "histories": f"{self._base_url}/assetHistories/{symbol}?range={range_param}&interval=1d",
            "fundamentals": f"{self._base_url}/assetFundamentals/{symbol}",
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            tasks = [client.get(url, auth=self._auth) for url in urls.values()]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

        data_bundle: Dict[str, Any] = {"symbol": symbol}

        for key, response in zip(urls.keys(), responses):
            if isinstance(response, Exception):
                data_bundle[key] = None
                continue

            if response.status_code != 200:
                data_bundle[key] = None
                continue

            try:
                data_bundle[key] = response.json()
            except ValueError:
                data_bundle[key] = None

        return data_bundle
