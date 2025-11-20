from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import make_scorer, mean_squared_error

from .feature_store import FeatureStore
from .train_buyhold import engineer_targets

try:
    from xgboost import XGBRegressor
except ImportError as exc:
    raise SystemExit("xgboost não instalado. Rode `pip install -r ml/requirements.txt`.") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Otimização de hiperparâmetros do modelo Buy & Hold")
    parser.add_argument("--train-until", default="2022-12-31", help="Data limite para treino (YYYY-MM-DD)")
    parser.add_argument("--n-iter", type=int, default=20, help="Número de combinações aleatórias")
    parser.add_argument("--cv", type=int, default=3, help="Número de folds no cross-validation")
    parser.add_argument("--output", default="models/buyhold_xgb_optimized.pkl", help="Arquivo para salvar o melhor modelo")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    store = FeatureStore()
    df = store.load_silver_dataset()
    df["date"] = pd.to_datetime(df["date"])
    cutoff = pd.to_datetime(args.train_until)
    df = df[df["date"] <= cutoff].copy()
    if df.empty:
        raise SystemExit("Dataset vazio após aplicar corte temporal. Rode ingest novamente ou ajuste o corte.")

    X, y = engineer_targets(df)

    param_grid: Dict[str, Any] = {
        "n_estimators": [100, 500, 1000],
        "max_depth": [3, 5, 7, 9],
        "learning_rate": [0.01, 0.05, 0.1],
        "subsample": [0.6, 0.8, 1.0],
        "colsample_bytree": [0.6, 0.8, 1.0],
    }

    base_model = XGBRegressor(
        objective="reg:squarederror",
        n_jobs=4,
        tree_method="hist",
        eval_metric="rmse",
    )

    scorer = make_scorer(mean_squared_error, greater_is_better=False)
    search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_grid,
        n_iter=args.n_iter,
        scoring=scorer,
        cv=args.cv,
        n_jobs=4,
        verbose=2,
        random_state=42,
    )

    print(f"[OPTIMIZER] Iniciando busca com {args.n_iter} combinações...")
    search.fit(X, y)

    best_model: XGBRegressor = search.best_estimator_
    print("[OPTIMIZER] Melhores parâmetros encontrados:")
    for key, value in search.best_params_.items():
        print(f" - {key}: {value}")
    print(f"[OPTIMIZER] Score (neg MSE): {search.best_score_:.6f}")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": best_model,
            "best_params": search.best_params_,
            "train_until": cutoff.strftime("%Y-%m-%d"),
        },
        args.output,
    )
    print(f"[OPTIMIZER] Modelo salvo em {args.output}")


if __name__ == "__main__":
    main()
