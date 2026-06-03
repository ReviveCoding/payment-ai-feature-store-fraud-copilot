from __future__ import annotations
import pandas as pd

MODEL_FEATURES = [
    "amount", "amount_log", "cross_border_flag", "rule_risk_prior", "txn_count_prior",
    "amount_sum_prior", "failed_txn_rate_prior", "amount_zscore_account", "new_device_flag",
    "new_beneficiary_flag", "high_risk_corridor_flag", "rejected_flag", "processing_time_secs"
]


def build_training_set(features: pd.DataFrame) -> pd.DataFrame:
    keep = ["event_id", "event_time", "dataset_source", "risk_label", "fraud_type_proxy"] + MODEL_FEATURES
    df = features[keep].copy().sort_values("event_time").reset_index(drop=True)
    for col in MODEL_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def validate_point_in_time(features: pd.DataFrame) -> dict:
    # Prior counts should never exceed previous row count within account.
    temp = features.sort_values(["account_id_hash", "event_time", "event_id"]).copy()
    expected = temp.groupby("account_id_hash").cumcount()
    ok = (temp["txn_count_prior"].astype(int).values == expected.values).all()
    return {
        "point_in_time_valid": bool(ok),
        "checked_rows": int(len(temp)),
        "rule": "txn_count_prior equals number of prior events within account",
    }
