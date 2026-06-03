from __future__ import annotations
import pandas as pd
from src.modeling.metrics import evaluate_scores


def simulate_policy_scenarios(preds: pd.DataFrame, capacity_fraction: float = 0.05) -> pd.DataFrame:
    scenarios = {
        "vanilla_best": "score_vanilla_best",
        "calibrated": "score_calibrated",
        "residual_corrected": "score_residual_corrected",
        "envelope_pruned": "score_envelope_pruned",
    }
    rows = []
    for name, col in scenarios.items():
        if col not in preds.columns:
            continue
        metrics = evaluate_scores(preds["risk_label"].values, preds[col].values, preds["amount"].values, capacity_fraction)
        metrics["scenario"] = name
        rows.append(metrics)
    out = pd.DataFrame(rows)
    if not out.empty:
        out["decision_score"] = (
            out["fraud_loss_capture_rate"] * 0.40
            + out["precision_at_capacity"] * 0.25
            + out["recall_at_capacity"] * 0.20
            - out["ece"] * 0.10
            - out["review_burden"] * 0.05
        )
    return out.sort_values("decision_score", ascending=False).reset_index(drop=True) if not out.empty else out
