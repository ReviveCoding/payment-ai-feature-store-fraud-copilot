from __future__ import annotations
import hashlib
from pathlib import Path
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype
from src.utils import write_json


def _stable_hash_frame(df: pd.DataFrame, cols: list[str]) -> str:
    """Create a deterministic content hash for local idempotence checks."""
    if df.empty:
        return "empty"
    work = df[cols].copy()
    for c in work.columns:
        if is_datetime64_any_dtype(work[c]):
            work[c] = pd.to_datetime(work[c]).dt.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            # Pandas extension dtypes such as StringDtype in pandas 3.x are
            # intentionally cast to string only at hashing time. This keeps
            # the idempotence hash stable across pandas/numpy versions without
            # changing the upstream feature table.
            work[c] = work[c].astype("string").fillna("<NA>")
    work = work.sort_values(cols).reset_index(drop=True)
    payload = work.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def evaluate_data_quality(events: pd.DataFrame, features: pd.DataFrame, out_dir: str | Path) -> dict:
    """Evaluate production-style data quality gates on the canonical and feature tables.

    This is intentionally local/offline. It mirrors the type of data-quality baseline
    a production feature pipeline would need before batch scoring or training.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    required_event_cols = ["event_id", "event_time", "account_id_hash", "amount", "risk_label", "dataset_source"]
    required_feature_cols = [
        "event_id", "event_time", "account_id_hash", "amount", "rule_risk_prior",
        "txn_count_prior", "failed_txn_rate_prior", "amount_zscore_account"
    ]
    event_nulls = {c: float(events[c].isna().mean()) if c in events.columns else 1.0 for c in required_event_cols}
    feature_nulls = {c: float(features[c].isna().mean()) if c in features.columns else 1.0 for c in required_feature_cols}
    duplicate_event_rate = float(events["event_id"].duplicated().mean()) if "event_id" in events.columns and len(events) else 1.0
    duplicate_feature_rate = float(features["event_id"].duplicated().mean()) if "event_id" in features.columns and len(features) else 1.0
    amount = pd.to_numeric(features.get("amount", pd.Series(dtype=float)), errors="coerce")
    amount_stats = {
        "min": float(amount.min()) if len(amount) else 0.0,
        "p50": float(amount.quantile(0.50)) if len(amount) else 0.0,
        "p95": float(amount.quantile(0.95)) if len(amount) else 0.0,
        "max": float(amount.max()) if len(amount) else 0.0,
        "non_positive_rate": float((amount <= 0).mean()) if len(amount) else 1.0,
    }
    source_counts = events.get("dataset_source", pd.Series(dtype=str)).value_counts(dropna=False).to_dict()
    feature_counts = features.get("dataset_source", pd.Series(dtype=str)).value_counts(dropna=False).to_dict()
    hash_cols = [c for c in ["event_id", "event_time", "account_id_hash", "amount", "rule_risk_prior", "txn_count_prior"] if c in features.columns]
    deterministic_feature_hash = _stable_hash_frame(features, hash_cols)
    checks = {
        "required_event_columns_present": all(c in events.columns for c in required_event_cols),
        "required_feature_columns_present": all(c in features.columns for c in required_feature_cols),
        "event_duplicate_rate_ok": duplicate_event_rate == 0.0,
        "feature_duplicate_rate_ok": duplicate_feature_rate == 0.0,
        "event_null_rate_ok": all(v <= 0.05 for v in event_nulls.values()),
        "feature_null_rate_ok": all(v <= 0.05 for v in feature_nulls.values()),
        "amount_values_positive": amount_stats["non_positive_rate"] == 0.0,
        "dataset_sources_present": len(source_counts) >= 1,
        "feature_sources_present": len(feature_counts) >= 1,
    }
    status = "PASS" if all(checks.values()) else "REVIEW"
    result = {
        "status": status,
        "rows": {"events": int(len(events)), "features": int(len(features))},
        "null_rates": {"events": event_nulls, "features": feature_nulls},
        "duplicate_rates": {"events": duplicate_event_rate, "features": duplicate_feature_rate},
        "amount_stats": amount_stats,
        "source_counts": {"events": source_counts, "features": feature_counts},
        "deterministic_feature_hash": deterministic_feature_hash,
        "checks": checks,
    }
    write_json(out_dir / "data_quality_baseline.json", result)
    return result


def evaluate_backfill_idempotence(features_first: pd.DataFrame, features_second: pd.DataFrame, out_dir: str | Path) -> dict:
    """Check whether a simulated rerun produces the same feature content."""
    out_dir = Path(out_dir)
    hash_cols = [c for c in ["event_id", "event_time", "account_id_hash", "amount", "rule_risk_prior", "txn_count_prior", "failed_txn_rate_prior"] if c in features_first.columns]
    first_hash = _stable_hash_frame(features_first, hash_cols)
    second_hash = _stable_hash_frame(features_second, hash_cols)
    result = {
        "status": "PASS" if first_hash == second_hash and len(features_first) == len(features_second) else "REVIEW",
        "first_rows": int(len(features_first)),
        "second_rows": int(len(features_second)),
        "first_hash": first_hash,
        "second_hash": second_hash,
        "rule": "A deterministic rerun over the same inputs should produce identical feature hashes and row counts.",
    }
    write_json(out_dir / "backfill_idempotence.json", result)
    return result
