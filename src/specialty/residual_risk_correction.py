from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from src.modeling.metrics import evaluate_scores


def _score_for_utility(metrics: dict) -> float:
    return float(
        0.30 * metrics.get("pr_auc", 0.0)
        + 0.25 * metrics.get("precision_at_capacity", 0.0)
        + 0.30 * metrics.get("fraud_loss_capture_rate", 0.0)
        - 0.15 * metrics.get("ece", 1.0)
    )


def apply_residual_correction(preds: pd.DataFrame, capacity_fraction: float = 0.05) -> tuple[pd.DataFrame, dict]:
    """Mechanism-informed residual correction.

    Blends the selected operating champion with an interpretable rule-risk prior.
    Alpha is selected by operational utility rather than PR-AUC alone.
    """
    df = preds.copy()
    y = df["risk_label"].astype(int).values
    model_col = "score_operating_champion" if "score_operating_champion" in df.columns else "score_calibrated"
    model = df[model_col].values
    prior = df["rule_risk_prior"].clip(0, 1).values
    best = {"alpha": 1.0, "utility": -1.0, "metrics": None}
    for alpha in np.linspace(0.40, 0.98, 15):
        score = np.clip(alpha * model + (1 - alpha) * prior, 0, 1)
        metrics = evaluate_scores(y, score, df["amount"].values, capacity_fraction)
        util = _score_for_utility(metrics)
        if util > best["utility"]:
            best = {"alpha": float(alpha), "utility": float(util), "metrics": metrics}
    df["score_residual_corrected"] = np.clip(best["alpha"] * model + (1 - best["alpha"]) * prior, 0, 1)
    metrics = best["metrics"] or evaluate_scores(y, df["score_residual_corrected"].values, df["amount"].values, capacity_fraction)
    metrics["selected_alpha"] = best["alpha"]
    metrics["base_score_column"] = model_col
    metrics["policy_utility"] = _score_for_utility(metrics)
    return df, metrics
