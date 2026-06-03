from __future__ import annotations
import numpy as np
import pandas as pd
from src.modeling.metrics import evaluate_scores


def run_score_stress_tests(preds: pd.DataFrame, score_col: str = "score_envelope_pruned", capacity_fraction: float = 0.05) -> dict:
    """Small-data robustness checks for operational score behavior.

    These checks are intentionally lightweight and local-runnable. They do not
    replace production stress testing, but they demonstrate the evaluation habit:
    amount spikes, prior-signal suppression, and shifted score distributions.
    """
    df = preds.copy()
    y = df["risk_label"].astype(int).values
    amount = df["amount"].astype(float).values
    base = evaluate_scores(y, df[score_col].values, amount, capacity_fraction)

    # 1) Amount shock: important because payment fraud review often cares about loss capture.
    shocked_amount = amount.copy()
    high_amount_idx = np.argsort(-amount)[: max(1, int(0.05 * len(amount)))]
    shocked_amount[high_amount_idx] *= 1.5
    amount_shock = evaluate_scores(y, df[score_col].values, shocked_amount, capacity_fraction)

    # 2) Score drift: simulate mild score compression that can happen after calibration drift.
    compressed_score = np.clip(0.85 * df[score_col].values + 0.075, 0, 1)
    score_drift = evaluate_scores(y, compressed_score, amount, capacity_fraction)

    # 3) Weak-signal ablation: compare to residual score if available.
    if "score_residual_corrected" in df.columns:
        no_envelope = evaluate_scores(y, df["score_residual_corrected"].values, amount, capacity_fraction)
    else:
        no_envelope = base

    return {
        "base": base,
        "amount_shock": amount_shock,
        "score_compression_drift": score_drift,
        "without_envelope_pruning": no_envelope,
        "notes": [
            "Small-data stress tests are sanity checks, not production validation.",
            "Amount-shock evaluates sensitivity of fraud-loss capture.",
            "Score-compression drift evaluates whether ranking metrics are stable under mild calibration drift.",
        ],
    }
