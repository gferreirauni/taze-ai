from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any

import joblib
import numpy as np
import pandas as pd

from .config import settings
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "silver"
MODEL_PATH = BASE_DIR / "models" / "buyhold_xgb.pkl"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

INITIAL_CAPITAL = 10_000.0
BACKTEST_DAYS = 365 * 2  # ~2 anos
MIN_RET = -0.15
MAX_RET = 0.15
RISK_LOW = 0.015
RISK_HIGH = 0.035

PROFILE_RULES = {
    "Conservador": {
        "buy": lambda score, risk_label: score > 8.5 and risk_label == "BAIXO",
        "sell": lambda score, risk_label: score < 7.5,
    },
    "Moderado": {
        "buy": lambda score, risk_label: score > 7.0,
        "sell": lambda score, risk_label: score < 5.0,
    },
    "Agressivo": {
        "buy": lambda score, risk_label: score > 6.0 or (score > 5.0 and risk_label == "ALTO"),
        "sell": lambda score, risk_label: score < 3.5,
    },
}


def classify_risk(value: float) -> str:
    if value < RISK_LOW:
        return "BAIXO"
    if value < RISK_HIGH:
        return "MODERADO"
    return "ALTO"


def load_model() -> Tuple[any, List[str]]:
    bundle = joblib.load(MODEL_PATH)
    if isinstance(bundle, dict) and "model" in bundle:
        model = bundle["model"]
        feature_names = bundle.get("feature_names") or getattr(model, "feature_names_in_", [])
    else:
        model = bundle
        feature_names = getattr(model, "feature_names_in_", [])

    if feature_names is None:
        feature_names_list: List[str] = []
    else:
        feature_names_list = list(feature_names)

    if len(feature_names_list) == 0:
        raise RuntimeError("Não foi possível determinar a lista de features do modelo.")

    return model, feature_names_list


def load_silver_frame(symbol: str) -> pd.DataFrame:
    files = sorted(DATA_DIR.glob(f"{symbol}_*.parquet"))
    if not files:
        raise FileNotFoundError(f"Nenhum dataset silver encontrado para {symbol}. Rode ml/ingest.py primeiro.")

    df = pd.read_parquet(files[-1])
    df["date"] = pd.to_datetime(df["date"])
    cutoff = df["date"].max() - timedelta(days=BACKTEST_DAYS)
    df = df[df["date"] >= cutoff].copy()
    df.sort_values("date", inplace=True)
    if df.empty:
        raise ValueError(f"Dataset de {symbol} ficou vazio após aplicar janela de {BACKTEST_DAYS} dias.")
    return df


def prediction_to_score(prediction: float, risk_value: float) -> float:
    clamped = max(MIN_RET, min(MAX_RET, prediction))
    normalized = (clamped - MIN_RET) / (MAX_RET - MIN_RET)
    base_score = normalized * 10

    if risk_value < 0.015:
        penalty = 0.0
    elif risk_value < 0.035:
        penalty = 0.4
    else:
        penalty = 0.8

    return float(np.clip(base_score - penalty, 0.0, 10.0))


def simulate_strategy(
    df: pd.DataFrame,
    model,
    feature_names: List[str],
    buy_rule,
    sell_rule,
) -> Tuple[List[float], List[float], List[float], List[pd.Timestamp], Dict[str, Any]]:
    cash = INITIAL_CAPITAL
    shares = 0.0
    equity_curve: List[float] = []
    scores: List[float] = []
    dates: List[pd.Timestamp] = []
    trade_returns: List[float] = []
    trade_durations: List[int] = []
    total_trades = 0
    winning_trades = 0
    entry_date = None
    entry_price = 0.0
    max_score = float("-inf")
    score_sum = 0.0
    score_count = 0

    valid_prices = df[df["close"] > 0]
    if valid_prices.empty:
        raise ValueError("Nenhum preço válido encontrado para o backtest.")
    bh_shares = INITIAL_CAPITAL / float(valid_prices.iloc[0]["close"])
    bh_curve: List[float] = []

    for _, row in df.iterrows():
        price = float(row["close"])
        if price <= 0:
            continue

        dates.append(row["date"])
        features = row.reindex(feature_names).astype(float).fillna(0.0).values.reshape(1, -1)
        raw_pred = float(model.predict(features)[0])
        risk_value = float(row.get("volatility_21", 0.0))
        risk_label = classify_risk(risk_value)
        score = prediction_to_score(raw_pred, risk_value)
        scores.append(score)
        max_score = max(max_score, score)
        score_sum += score
        score_count += 1
        if buy_rule(score, risk_label) and cash > 0:
            shares = cash / price
            cash = 0.0
            entry_price = price
            entry_date = row["date"]
            total_trades += 1
        elif sell_rule(score, risk_label) and shares > 0:
            exit_value = shares * price
            cost = shares * entry_price
            cash += exit_value
            trade_return = (exit_value - cost) / cost if cost > 0 else 0
            trade_returns.append(trade_return)
            if trade_return > 0:
                winning_trades += 1
            if entry_date is not None:
                duration = (row["date"] - entry_date).days
                trade_durations.append(max(duration, 1))
            shares = 0.0
            entry_date = None
            entry_price = 0.0

        equity_curve.append(cash + shares * price)
        bh_curve.append(bh_shares * price)

    stats = {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "trade_returns": trade_returns,
        "trade_durations": trade_durations,
        "max_score": max_score if score_count else 0.0,
        "avg_score": (score_sum / score_count) if score_count else 0.0,
    }

    return equity_curve, bh_curve, scores, dates, stats


def maybe_plot(symbol: str, dates: List[pd.Timestamp], strategy_curve: List[float], bh_curve: List[float]) -> None:
    if plt is None:
        return
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(dates, strategy_curve, label="Taze AI", linewidth=2.2)
    ax.plot(dates, bh_curve, label="Buy & Hold", linestyle="--", linewidth=1.6)
    ax.set_title(f"Backtest {symbol} - Últimos 2 anos")
    ax.set_ylabel("Patrimônio (R$)")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.autofmt_xdate()
    output_path = RESULTS_DIR / f"{symbol}_backtest.png"
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[BACKTEST] Gráfico salvo em {output_path}")


def run_backtest() -> None:
    model, feature_names = load_model()
    profile_totals: Dict[str, Dict[str, float]] = {
        name: {"alpha": 0.0, "count": 0.0} for name in PROFILE_RULES
    }

    for symbol in settings.tickers:
        df = load_silver_frame(symbol)

        missing_features = [col for col in feature_names if col not in df.columns]
        if missing_features:
            for col in missing_features:
                df[col] = 0.0

        print(f"\n[BACKTEST] --- {symbol} ---")
        for profile, rules in PROFILE_RULES.items():
            strategy_curve, bh_curve, _, valid_dates, stats = simulate_strategy(
                df, model, feature_names, rules["buy"], rules["sell"]
            )
            if not strategy_curve:
                print(f"[{profile}] Sem dados válidos para {symbol}.")
                continue

            final_strategy = strategy_curve[-1]
            final_bh = bh_curve[-1]

            perf_strategy = (final_strategy / INITIAL_CAPITAL - 1) * 100
            perf_bh = (final_bh / INITIAL_CAPITAL - 1) * 100
            alpha = perf_strategy - perf_bh

            profile_totals[profile]["alpha"] += alpha
            profile_totals[profile]["count"] += 1

            total_trades = stats["total_trades"]
            winning_trades = stats["winning_trades"]
            trade_returns = stats["trade_returns"]
            trade_durations = stats["trade_durations"]
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
            avg_duration = np.mean(trade_durations) if trade_durations else 0.0
            avg_trade_return = np.mean(trade_returns) * 100 if trade_returns else 0.0
            max_score = stats["max_score"]
            avg_score = stats["avg_score"]

            summary = (
                f"[{profile}] Carteira: R$ {final_strategy:,.2f} ({perf_strategy:+.2f}%) | "
                f"Win Rate: {win_rate:.1f}% | Duração Média: {avg_duration:.1f} dias | "
                f"Lucro Médio por Trade: {avg_trade_return:+.2f}% | "
                f"Max Score: {max_score:.1f} | Avg Score: {avg_score:.1f}"
            )
            print(summary)

            if profile == "Moderado":
                maybe_plot(f"{symbol}-{profile}", valid_dates, strategy_curve, bh_curve)

    print("\n[BACKTEST] ===== Resumo por Perfil =====")
    for profile, stats in profile_totals.items():
        count = stats["count"] or 1.0
        avg_alpha = stats["alpha"] / count
        print(f"{profile}: Alpha médio = {avg_alpha:+.2f}% (sobre {int(stats['count'])} ativos)")


if __name__ == "__main__":
    if not MODEL_PATH.exists():
        raise SystemExit(f"Modelo não encontrado em {MODEL_PATH}. Treine primeiro com python ml/train_buyhold.py")
    run_backtest()
