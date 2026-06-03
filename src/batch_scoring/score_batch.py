from __future__ import annotations
from pathlib import Path
import pandas as pd


def build_batch_scoring_sample(preds: pd.DataFrame, out_path: str | Path, score_col: str = "score_final_operating_policy", n: int = 50) -> dict:
    """Create a batch scoring artifact with approve/review/block decisions."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    work = preds.sort_values(score_col, ascending=False).head(min(n, len(preds))).copy()
    def decision(s: float) -> str:
        if s >= 0.80:
            return "block_or_escalate"
        if s >= 0.45:
            return "human_review"
        return "auto_approve"
    keep = [c for c in ["event_id", "event_time", "dataset_source", "fraud_type_proxy", "amount", "risk_label", score_col] if c in work.columns]
    out = work[keep].copy()
    out["decision"] = out[score_col].apply(decision)
    out["decision_reason"] = out.apply(lambda r: f"score={r[score_col]:.3f}; amount={r.get('amount', 0):.2f}; proxy={r.get('fraud_type_proxy', 'unknown')}", axis=1)
    out.to_csv(out_path, index=False)
    return {
        "status": "PASS",
        "rows_scored": int(len(out)),
        "score_column": score_col,
        "decision_counts": out["decision"].value_counts().to_dict(),
        "artifact": str(out_path),
        "claim_boundary": "Offline batch scoring sample only. Not a production decision service.",
    }
