from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from src.utils import write_json


def build_monitoring_baseline(train_df: pd.DataFrame, preds_df: pd.DataFrame, feature_names: list[str], out_dir: str | Path) -> dict:
    """Generate local Model-Monitor-style baseline statistics and constraints.

    The artifact is compatible with a governance review. It is not an actual
    SageMaker Model Monitor schedule unless executed on AWS.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stats = {}
    constraints = {}
    for col in feature_names:
        if col not in train_df.columns:
            continue
        s = pd.to_numeric(train_df[col], errors="coerce")
        stats[col] = {
            "count": int(s.notna().sum()),
            "missing_rate": float(s.isna().mean()),
            "mean": float(s.mean()) if s.notna().any() else 0.0,
            "std": float(s.std()) if s.notna().sum() > 1 else 0.0,
            "p01": float(s.quantile(0.01)) if s.notna().any() else 0.0,
            "p50": float(s.quantile(0.50)) if s.notna().any() else 0.0,
            "p99": float(s.quantile(0.99)) if s.notna().any() else 0.0,
        }
        constraints[col] = {
            "max_missing_rate": 0.20,
            "expected_min": stats[col]["p01"],
            "expected_max": stats[col]["p99"],
            "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold",
        }
    score_col = "score_final_operating_policy" if "score_final_operating_policy" in preds_df.columns else None
    score_stats = {}
    if score_col:
        score = pd.to_numeric(preds_df[score_col], errors="coerce")
        score_stats = {
            "score_column": score_col,
            "mean": float(score.mean()),
            "std": float(score.std()) if score.notna().sum() > 1 else 0.0,
            "p05": float(score.quantile(0.05)),
            "p50": float(score.quantile(0.50)),
            "p95": float(score.quantile(0.95)),
            "high_score_rate_0_8": float((score >= 0.8).mean()),
        }
    baseline = {
        "status": "PASS",
        "baseline_type": "local_model_monitor_style_baseline",
        "feature_statistics": stats,
        "feature_constraints": constraints,
        "score_distribution": score_stats,
        "claim_boundary": "Local monitoring baseline only. Not an active SageMaker Model Monitor schedule unless deployed on AWS.",
    }
    write_json(out_dir / "data_quality_constraints.json", constraints)
    write_json(out_dir / "model_monitoring_baseline.json", baseline)
    return baseline
