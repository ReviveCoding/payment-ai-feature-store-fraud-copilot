from __future__ import annotations
import numpy as np
import pandas as pd
from src.modeling.metrics import evaluate_scores


def operating_utility(metrics: dict) -> float:
    return float(
        0.30 * metrics.get("pr_auc", 0.0)
        + 0.25 * metrics.get("precision_at_capacity", 0.0)
        + 0.30 * metrics.get("fraud_loss_capture_rate", 0.0)
        - 0.15 * metrics.get("ece", 1.0)
    )


def select_final_policy(preds: pd.DataFrame, candidate_score_cols: list[str], capacity_fraction: float = 0.05) -> tuple[pd.DataFrame, dict]:
    """Select the final operating score from champion/challenger candidates.

    This prevents an experimental specialty module from degrading the final release
    if it improves one metric but worsens calibration or review utility.
    """
    df = preds.copy()
    rows = []
    best = None
    for col in candidate_score_cols:
        if col not in df.columns:
            continue
        metrics = evaluate_scores(df["risk_label"].values, df[col].values, df["amount"].values, capacity_fraction)
        metrics["candidate_score_column"] = col
        metrics["policy_utility"] = operating_utility(metrics)
        rows.append(metrics)
        if best is None or metrics["policy_utility"] > best["policy_utility"]:
            best = metrics
    if best is None:
        raise ValueError("No candidate score columns were available for final policy selection.")
    df["score_final_operating_policy"] = df[best["candidate_score_column"]]
    final = dict(best)
    final["selected_policy_name"] = best["candidate_score_column"].replace("score_", "")
    final["candidate_count"] = len(rows)
    final["candidate_metrics"] = rows
    return df, final
