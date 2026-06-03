from __future__ import annotations
from pathlib import Path
import pandas as pd
from src.data_generation.generate_sample_data import generate_public_style_fraud_sample


def load_or_generate_public_fraud(sample_path: str | Path | None = None, n: int = 2500) -> pd.DataFrame:
    if sample_path and Path(sample_path).exists():
        return pd.read_csv(sample_path, parse_dates=["event_time"])
    return generate_public_style_fraud_sample(n=n)


def load_user_supplied_csv(path: str | Path, source_name: str) -> pd.DataFrame:
    """Adapter scaffold for user-supplied PaySim, IEEE-CIS, or BAF style files.

    This function intentionally performs only safe common-column mapping. Dataset-specific
    production use should extend this adapter with explicit schema checks.
    """
    path = Path(path)
    raw = pd.read_csv(path)
    cols = {c.lower(): c for c in raw.columns}
    amount_col = cols.get("amount") or cols.get("transactionamt") or cols.get("transactionamt")
    label_col = cols.get("isfraud") or cols.get("fraud_bool") or cols.get("isfraud")
    if amount_col is None or label_col is None:
        raise ValueError(f"Cannot map {path}; amount and label columns were not found.")
    n = len(raw)
    event_time = pd.Timestamp("2025-01-01") + pd.to_timedelta(range(n), unit="m")
    return pd.DataFrame({
        "dataset_source": source_name,
        "event_id": [f"{source_name}-{i:07d}" for i in range(n)],
        "event_time": event_time,
        "account_id_hash": [f"acct_{i % 1000:05d}" for i in range(n)],
        "customer_id_hash": [f"cust_{i % 1000:05d}" for i in range(n)],
        "device_id_hash": [f"dev_{i % 350:05d}" for i in range(n)],
        "counterparty_id_hash": [f"cp_{i % 800:05d}" for i in range(n)],
        "amount": pd.to_numeric(raw[amount_col], errors="coerce").fillna(0),
        "currency": "USD",
        "channel": "public_dataset",
        "payment_type": "public_dataset_transaction",
        "payment_status": "ACSP",
        "failure_reason": "",
        "fraud_type_proxy": "public_label_proxy",
        "risk_label": pd.to_numeric(raw[label_col], errors="coerce").fillna(0).astype(int),
        "debtor_country": "UNK",
        "creditor_country": "UNK",
        "processing_time_secs": 0,
        "purpose_code": "UNK",
        "source_file": str(path.name),
    })
