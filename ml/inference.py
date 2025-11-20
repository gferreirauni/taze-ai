from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np
import pandas as pd


class PredictiveService:
    """
    Serviço de inferência para o modelo proprietário de Buy & Hold.
    Pode operar em modo degradado caso o modelo ainda não tenha sido treinado.
    """

    def __init__(self, model_path: str | Path | None = None) -> None:
        default_path = Path("ml/models/buyhold_xgb.pkl")
        self.model_path = Path(model_path) if model_path else default_path
        self.model = None
        self.metadata: Dict[str, Any] = {}
        self.feature_names: list[str] = []
        self._load_model()

    def _load_model(self) -> None:
        if not self.model_path.exists():
            print(f"[PREDICTIVE] Modelo não encontrado em {self.model_path}. Operando em modo degradado.")
            return

        try:
            bundle = joblib.load(self.model_path)
            if isinstance(bundle, dict) and "model" in bundle:
                self.model = bundle["model"]
                self.metadata = {k: v for k, v in bundle.items() if k != "model"}
            else:
                self.model = bundle
                self.metadata = {}

            if hasattr(self.model, "feature_names_in_"):
                self.feature_names = list(self.model.feature_names_in_)
            else:
                self.feature_names = self.metadata.get("feature_names", [])

            print(f"[PREDICTIVE] Modelo carregado com sucesso ({self.model_path}).")
        except Exception as exc:
            print(f"[PREDICTIVE] Falha ao carregar modelo: {exc}. Operando em modo degradado.")
            self.model = None

    def predict_score(self, symbol: str, stock_snapshot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retorna o score proprietário (0-10) baseado nos dados atuais do ativo.
        """
        if self.model is None:
            return None

        feature_vector = self._build_feature_vector(stock_snapshot)
        if feature_vector is None:
            return None

        if self.feature_names:
            ordered = [feature_vector.get(name, 0.0) for name in self.feature_names]
        else:
            ordered = list(feature_vector.values())

        X = np.array(ordered, dtype=np.float32).reshape(1, -1)

        try:
            raw_pred = float(self.model.predict(X)[0])
        except Exception as exc:
            print(f"[PREDICTIVE] Falha ao gerar previsão para {symbol}: {exc}")
            return None

        score = self._prediction_to_score(raw_pred)
        return {
            "score": round(score, 2),
            "raw_prediction": raw_pred,
            "horizon_days": int(self.metadata.get("horizon_days", 90)),
            "source": "taze_ml_buyhold",
        }

    def _build_feature_vector(self, stock_snapshot: Dict[str, Any]) -> Optional[Dict[str, float]]:
        history = stock_snapshot.get("history") or []
        if not history:
            return None

        df = pd.DataFrame(history)
        if "value" not in df:
            return None

        df = df.rename(columns={"value": "close"})
        df["close"] = df["close"].astype(float)
        df["close_ma_5"] = df["close"].rolling(window=5, min_periods=1).mean()
        df["close_ma_20"] = df["close"].rolling(window=20, min_periods=1).mean()
        df["close_std_20"] = df["close"].rolling(window=20, min_periods=1).std().fillna(0)
        df["daily_return"] = df["close"].pct_change().fillna(0)
        df["volume"] = 0.0  # Sem volume no snapshot atual
        df["volume_ma_20"] = 0.0

        latest = df.iloc[-1]

        features: Dict[str, float] = {
            "close": float(latest["close"]),
            "close_ma_5": float(latest["close_ma_5"]),
            "close_ma_20": float(latest["close_ma_20"]),
            "close_std_20": float(latest["close_std_20"]),
            "daily_return": float(latest["daily_return"]),
            "volume": 0.0,
            "volume_ma_20": 0.0,
        }

        fundamentals = stock_snapshot.get("fundamentals") or {}
        for key, value in fundamentals.items():
            feature_key = f"fund_{key}"
            try:
                features[feature_key] = float(value)
            except (TypeError, ValueError):
                continue

        return features

    def _prediction_to_score(self, prediction: float) -> float:
        """
        Converte retorno esperado em score 0-10.
        Valores entre -15% e +15% são mapeados linearmente.
        """
        min_ret, max_ret = -0.15, 0.15
        clamped = max(min_ret, min(max_ret, prediction))
        normalized = (clamped - min_ret) / (max_ret - min_ret)  # 0..1
        return normalized * 10
