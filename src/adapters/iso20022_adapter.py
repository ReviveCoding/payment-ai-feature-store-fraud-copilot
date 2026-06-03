from __future__ import annotations
from pathlib import Path
import zipfile
import pandas as pd


def load_iso20022_zip(path: str | Path) -> pd.DataFrame:
    """Load the local synthetic ISO 20022 zip if available.

    Expected files: iso20022_analytics.csv, pacs008.csv, pacs002.csv.
    Returns canonical-like rows.
    """
    path = Path(path)
    if not path.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(path) as z:
        target = "iso20022_analytics.csv" if "iso20022_analytics.csv" in z.namelist() else z.namelist()[0]
        with z.open(target) as f:
            df = pd.read_csv(f)
    if df.empty:
        return df
    out = pd.DataFrame({
        "dataset_source": "synthetic_iso20022_local",
        "event_id": df.get("MessageId", pd.Series(range(len(df)))).astype(str),
        "event_time": pd.to_datetime(df.get("TxDateTime"), errors="coerce"),
        "account_id_hash": "dbtr_" + df.get("DbtrAgtBIC", "UNK").astype(str),
        "customer_id_hash": "dbtr_" + df.get("DbtrAgtBIC", "UNK").astype(str),
        "device_id_hash": "iso_device_unknown",
        "counterparty_id_hash": "cdtr_" + df.get("CdtrAgtBIC", "UNK").astype(str),
        "amount": pd.to_numeric(df.get("InstdAmt"), errors="coerce").fillna(0),
        "currency": df.get("Currency", "UNK").astype(str),
        "channel": "iso20022",
        "payment_type": "pacs008_credit_transfer",
        "payment_status": df.get("TxSts", "UNKNOWN").astype(str),
        "failure_reason": df.get("RejectionReason", "").fillna("").astype(str),
        "fraud_type_proxy": "none",
        "risk_label": (df.get("TxSts", "ACSP").astype(str).isin(["RJCT", "PDNG"])).astype(int),
        "debtor_country": df.get("DbtrCountry", "UNK").astype(str),
        "creditor_country": df.get("CdtrCountry", "UNK").astype(str),
        "processing_time_secs": pd.to_numeric(df.get("ProcessingTimeSecs"), errors="coerce").fillna(0),
        "purpose_code": df.get("PurposeCode", "UNK").astype(str),
        "source_file": str(path.name),
    })
    return out.dropna(subset=["event_time"]).reset_index(drop=True)
