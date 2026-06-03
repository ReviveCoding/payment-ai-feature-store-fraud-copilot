from __future__ import annotations
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from src.feature_store.point_in_time_join import MODEL_FEATURES


def compute_feature_importance(model_path: str | Path, test_df: pd.DataFrame, out_dir: str | Path, max_rows: int = 600) -> dict:
    """Compute a small-data permutation importance report for the operating champion."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model = joblib.load(model_path)
    sample = test_df.sort_values("event_time").tail(min(max_rows, len(test_df))).copy()
    X = sample[MODEL_FEATURES]
    y = sample["risk_label"].astype(int)
    try:
        perm = permutation_importance(model, X, y, scoring="average_precision", n_repeats=5, random_state=42, n_jobs=1)
        imp = pd.DataFrame({
            "feature": MODEL_FEATURES,
            "importance_mean_pr_auc_drop": perm.importances_mean,
            "importance_std": perm.importances_std,
        }).sort_values("importance_mean_pr_auc_drop", ascending=False)
        method = "permutation_importance_average_precision"
    except Exception as exc:
        # Robust fallback: simple absolute correlation with label.
        rows = []
        for f in MODEL_FEATURES:
            s = pd.to_numeric(X[f], errors="coerce").fillna(0)
            corr = float(abs(np.corrcoef(s, y)[0, 1])) if s.std() > 0 and y.std() > 0 else 0.0
            rows.append({"feature": f, "importance_mean_pr_auc_drop": corr, "importance_std": 0.0})
        imp = pd.DataFrame(rows).sort_values("importance_mean_pr_auc_drop", ascending=False)
        method = f"correlation_fallback_due_to_{type(exc).__name__}"
    imp.to_csv(out_dir / "feature_importance.csv", index=False)
    top = imp.head(8).to_dict(orient="records")
    return {
        "status": "PASS",
        "method": method,
        "rows_evaluated": int(len(sample)),
        "top_features": top,
        "artifact": str(out_dir / "feature_importance.csv"),
        "claim_boundary": "Local explainability diagnostic only; not a formal SHAP/enterprise model-risk explanation package.",
    }
