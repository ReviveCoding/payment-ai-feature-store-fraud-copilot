from __future__ import annotations
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score, precision_score, recall_score, brier_score_loss


def expected_calibration_error(y_true, y_score, bins: int = 10) -> float:
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    edges = np.linspace(0, 1, bins + 1)
    ece = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (y_score >= lo) & (y_score < hi if hi < 1 else y_score <= hi)
        if mask.any():
            acc = y_true[mask].mean()
            conf = y_score[mask].mean()
            ece += mask.mean() * abs(acc - conf)
    return float(ece)


def precision_recall_at_capacity(y_true, y_score, capacity_fraction: float = 0.05):
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score)
    k = max(1, int(np.ceil(len(y_score) * capacity_fraction)))
    idx = np.argsort(-y_score)[:k]
    preds = np.zeros_like(y_true)
    preds[idx] = 1
    return {
        "precision_at_capacity": float(precision_score(y_true, preds, zero_division=0)),
        "recall_at_capacity": float(recall_score(y_true, preds, zero_division=0)),
        "review_burden": float(k / len(y_true)),
    }


def fraud_loss_metrics(y_true, y_score, amount, capacity_fraction: float = 0.05) -> dict:
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score)
    amount = np.asarray(amount, dtype=float)
    k = max(1, int(np.ceil(len(y_score) * capacity_fraction)))
    idx = np.argsort(-y_score)[:k]
    total_fraud_loss = float((amount * y_true).sum())
    captured = float((amount[idx] * y_true[idx]).sum())
    return {
        "fraud_loss_captured": captured,
        "total_fraud_loss": total_fraud_loss,
        "fraud_loss_capture_rate": float(captured / total_fraud_loss) if total_fraud_loss > 0 else 0.0,
        "false_negative_loss": float(total_fraud_loss - captured),
    }


def evaluate_scores(y_true, y_score, amount, capacity_fraction: float = 0.05) -> dict:
    y_true = np.asarray(y_true).astype(int)
    y_score = np.clip(np.asarray(y_score, dtype=float), 0, 1)
    out = {}
    out["pr_auc"] = float(average_precision_score(y_true, y_score)) if len(set(y_true)) > 1 else 0.0
    out["roc_auc"] = float(roc_auc_score(y_true, y_score)) if len(set(y_true)) > 1 else 0.5
    out.update(precision_recall_at_capacity(y_true, y_score, capacity_fraction))
    out.update(fraud_loss_metrics(y_true, y_score, amount, capacity_fraction))
    out["brier"] = float(brier_score_loss(y_true, y_score))
    out["ece"] = expected_calibration_error(y_true, y_score)
    return out
