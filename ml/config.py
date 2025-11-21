from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Configuração compartilhada entre ingestão, feature store e treinamento."""

    tradebox_user: str = field(default_factory=lambda: os.getenv("TRADEBOX_API_USER", "TradeBox"))
    tradebox_pass: str = field(default_factory=lambda: os.getenv("TRADEBOX_API_PASS", "TradeBoxAI@2025"))
    tradebox_base_url: str = field(default_factory=lambda: os.getenv("TRADEBOX_BASE_URL", "https://api.tradebox.com.br/v1"))
    tickers: List[str] = field(
        default_factory=lambda: [
            "VALE3", "PETR4", "ITUB4", "BBDC4", "BBAS3", "WEGE3",
            "ABEV3", "JBSS3", "SUZB3", "PRIO3", "CSAN3",
            "MGLU3", "LREN3", "VIIA3", "ASAI3", "CRFB3",
            "ELET3", "CMIG4", "EGIE3", "CPLE6", "RAIZ4",
            "B3SA3", "HAPV3", "RADL3", "RENT3", "CYRE3",
            "GGBR4", "GOAU4", "CSNA3", "USIM5"
        ]
    )
    history_range_days: int = int(os.getenv("ML_HISTORY_RANGE", "365"))
    concurrent_requests: int = int(os.getenv("ML_CONCURRENCY", "5"))
    data_root: Path = field(
        default_factory=lambda: Path(os.getenv("ML_OUTPUT_DIR", Path(__file__).resolve().parent / "data"))
    )

    def __post_init__(self) -> None:
        # Normalizar ticker list removendo espaços
        self.tickers = [ticker.strip().upper() for ticker in self.tickers if ticker.strip()]

        # Garantir estrutura bronze/silver/gold
        self.bronze_dir = self.data_root / "bronze"
        self.silver_dir = self.data_root / "silver"
        self.gold_dir = self.data_root / "gold"

        for directory in (self.data_root, self.bronze_dir, self.silver_dir, self.gold_dir):
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
