from __future__ import annotations
import pandas as pd

REQUIRED_COLUMNS = [
    "dataset_source", "event_id", "event_time", "account_id_hash", "counterparty_id_hash",
    "amount", "currency", "channel", "payment_type", "payment_status", "risk_label"
]


def validate_canonical(df: pd.DataFrame) -> dict:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    null_rates = {c: float(df[c].isna().mean()) for c in df.columns if c in REQUIRED_COLUMNS}
    return {
        "rows": int(len(df)),
        "missing_required_columns": missing,
        "required_null_rates": null_rates,
        "valid": not missing and all(v < 0.5 for v in null_rates.values()),
    }


def combine_sources(frames: list[pd.DataFrame]) -> pd.DataFrame:
    nonempty = [f for f in frames if f is not None and not f.empty]
    if not nonempty:
        raise ValueError("No non-empty data frames were provided.")
    df = pd.concat(nonempty, ignore_index=True, sort=False)
    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce")
    df = df.dropna(subset=["event_time"]).sort_values("event_time").reset_index(drop=True)
    for col in ["device_id_hash", "customer_id_hash", "failure_reason", "fraud_type_proxy", "debtor_country", "creditor_country", "purpose_code", "source_file"]:
        if col not in df.columns:
            df[col] = "not_available"
    if "processing_time_secs" not in df.columns:
        df["processing_time_secs"] = 0
    df["risk_label"] = pd.to_numeric(df["risk_label"], errors="coerce").fillna(0).astype(int)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df
