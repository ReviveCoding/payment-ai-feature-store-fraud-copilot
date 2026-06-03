from __future__ import annotations
import numpy as np
import pandas as pd
from src.modeling.metrics import evaluate_scores


def _operating_utility(metrics: dict) -> float:
    return float(
        0.30 * metrics.get("pr_auc", 0.0)
        + 0.25 * metrics.get("precision_at_capacity", 0.0)
        + 0.30 * metrics.get("fraud_loss_capture_rate", 0.0)
        - 0.15 * metrics.get("ece", 1.0)
    )


def _risk_region_metrics(df: pd.DataFrame, score_col: str, capacity_fraction: float) -> dict:
    k = max(1, int(np.ceil(len(df) * capacity_fraction)))
    idx = np.argsort(-df[score_col].values)[:k]
    reviewed_amount = float(df.iloc[idx]["amount"].sum())
    captured_fraud_amount = float((df.iloc[idx]["amount"] * df.iloc[idx]["risk_label"]).sum())
    total_fraud_amount = float((df["amount"] * df["risk_label"]).sum())
    precision_amount = captured_fraud_amount / reviewed_amount if reviewed_amount else 0.0
    recall_amount = captured_fraud_amount / total_fraud_amount if total_fraud_amount else 0.0
    return {
        "risk_region_recall_amount": recall_amount,
        "risk_region_precision_amount": precision_amount,
        "risk_region_f1_amount": float(2 * precision_amount * recall_amount / (precision_amount + recall_amount)) if (precision_amount + recall_amount) else 0.0,
    }


def apply_risk_envelope_pruning(preds: pd.DataFrame, capacity_fraction: float = 0.05) -> tuple[pd.DataFrame, dict]:
    """ABC-inspired high-recall risk envelope and bias-corrected pruning.

    Stage 1 inflates suspicious coverage with weak signals. Stage 2 performs a
    lightweight grid search over pruning weights to balance fraud-loss capture,
    precision, and calibration.
    """
    df = preds.copy()
    model_thr = np.quantile(df["score_residual_corrected"], 1 - max(0.10, capacity_fraction * 2))
    prior_thr = np.quantile(df["rule_risk_prior"], 0.90)
    envelope = (
        (df["score_residual_corrected"] >= model_thr)
        | (df["rule_risk_prior"] >= prior_thr)
        | (df["rejected_flag"] == 1)
        | ((df["new_device_flag"] == 1) & (df["amount_zscore_account"] > 1.0))
    )
    df["risk_envelope_flag"] = envelope.astype(int)

    y = df["risk_label"].values
    amount = df["amount"].values
    best = {"utility": -1.0, "score": None, "metrics": None, "weights": None}
    # Conservative grid, still deterministic and fast on small/local data.
    for env_boost in [0.08, 0.15, 0.22, 0.30]:
        for prior_weight in [0.00, 0.04, 0.08, 0.12]:
            score = np.clip(
                df["score_residual_corrected"].values * (1.0 + env_boost * df["risk_envelope_flag"].values)
                + prior_weight * df["rule_risk_prior"].values,
                0,
                1,
            )
            metrics = evaluate_scores(y, score, amount, capacity_fraction)
            metrics.update(_risk_region_metrics(df.assign(_tmp_score=score), "_tmp_score", capacity_fraction))
            metrics["envelope_rate"] = float(df["risk_envelope_flag"].mean())
            util = _operating_utility(metrics)
            if util > best["utility"]:
                best = {"utility": util, "score": score, "metrics": metrics, "weights": {"env_boost": env_boost, "prior_weight": prior_weight}}
    df["score_envelope_pruned"] = best["score"]
    metrics = best["metrics"]
    metrics["selected_weights"] = best["weights"]
    metrics["policy_utility"] = float(best["utility"])
    return df, metrics
