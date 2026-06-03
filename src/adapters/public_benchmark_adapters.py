from __future__ import annotations
from pathlib import Path
import gzip
import json
import pandas as pd


def _read_csv_any(path: str | Path, max_rows: int | None = None) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".gz":
        return pd.read_csv(path, nrows=max_rows, compression="gzip")
    return pd.read_csv(path, nrows=max_rows)


def _safe_series(df: pd.DataFrame, col: str | None, default, n: int):
    if col and col in df.columns:
        return df[col]
    return pd.Series([default] * n)


def _base_frame(df: pd.DataFrame, source_name: str, amount_col: str, label_col: str, *,
                event_id_col: str | None = None, time_col: str | None = None,
                account_col: str | None = None, device_col: str | None = None,
                counterparty_col: str | None = None) -> pd.DataFrame:
    n = len(df)
    if n == 0:
        return pd.DataFrame()
    if time_col and time_col in df.columns:
        event_time = pd.to_datetime(df[time_col], errors="coerce")
        if event_time.isna().all():
            event_time = pd.Timestamp("2025-01-01") + pd.to_timedelta(range(n), unit="m")
    else:
        event_time = pd.Timestamp("2025-01-01") + pd.to_timedelta(range(n), unit="m")

    amount = pd.to_numeric(df[amount_col], errors="coerce").fillna(0).clip(lower=0)
    label = pd.to_numeric(df[label_col], errors="coerce").fillna(0).astype(int).clip(0, 1)
    event_ids = _safe_series(df, event_id_col, None, n).astype(str) if event_id_col else pd.Series([f"{source_name}-{i:07d}" for i in range(n)])
    if event_id_col:
        event_ids = event_ids.where(event_ids.notna() & (event_ids != "nan"), pd.Series([f"{source_name}-{i:07d}" for i in range(n)]))

    acct = _safe_series(df, account_col, None, n) if account_col else pd.Series([i % max(10, min(2500, n // 5 + 1)) for i in range(n)])
    device = _safe_series(df, device_col, None, n) if device_col else pd.Series([i % max(10, min(600, n // 8 + 1)) for i in range(n)])
    cp = _safe_series(df, counterparty_col, None, n) if counterparty_col else pd.Series([(i * 7) % max(10, min(3000, n // 4 + 1)) for i in range(n)])

    out = pd.DataFrame({
        "dataset_source": source_name,
        "event_id": event_ids.astype(str),
        "event_time": event_time,
        "account_id_hash": "acct_" + acct.astype(str).str.replace(r"[^A-Za-z0-9_-]", "", regex=True).str[-32:],
        "customer_id_hash": "cust_" + acct.astype(str).str.replace(r"[^A-Za-z0-9_-]", "", regex=True).str[-32:],
        "device_id_hash": "dev_" + device.astype(str).str.replace(r"[^A-Za-z0-9_-]", "", regex=True).str[-32:],
        "counterparty_id_hash": "cp_" + cp.astype(str).str.replace(r"[^A-Za-z0-9_-]", "", regex=True).str[-32:],
        "amount": amount,
        "currency": "USD",
        "channel": "public_benchmark",
        "payment_type": "public_benchmark_transaction",
        "payment_status": "ACSP",
        "failure_reason": "",
        "fraud_type_proxy": label.map({1: "public_fraud_label", 0: "none"}),
        "risk_label": label,
        "debtor_country": "UNK",
        "creditor_country": "UNK",
        "processing_time_secs": 0.0,
        "purpose_code": "UNK",
        "source_file": source_name,
    })
    return out.dropna(subset=["event_time"]).reset_index(drop=True)


def load_paysim(path: str | Path, max_rows: int | None = None) -> pd.DataFrame:
    """Map a PaySim-style CSV into the canonical payment-event schema.

    Expected columns usually include step, type, amount, nameOrig, nameDest, isFraud.
    """
    df = _read_csv_any(path, max_rows)
    lower = {c.lower(): c for c in df.columns}
    amount_col = lower.get("amount")
    label_col = lower.get("isfraud") or lower.get("is_fraud")
    if amount_col is None or label_col is None:
        raise ValueError("PaySim adapter requires amount and isFraud columns.")
    out = _base_frame(df, "paysim_public", amount_col, label_col,
                      event_id_col=None, time_col=None,
                      account_col=lower.get("nameorig"), counterparty_col=lower.get("namedest"))
    if "type" in lower:
        out["payment_type"] = df[lower["type"]].astype(str)
    if "step" in lower:
        out["event_time"] = pd.Timestamp("2025-01-01") + pd.to_timedelta(pd.to_numeric(df[lower["step"]], errors="coerce").fillna(0), unit="h")
    out["source_file"] = str(Path(path).name)
    return out


def load_baf(path: str | Path, max_rows: int | None = None) -> pd.DataFrame:
    """Map a Bank Account Fraud Dataset Suite CSV into the canonical schema.

    Expected label is usually fraud_bool; amount may be absent in some BAF files, so this
    adapter creates a stable proxy amount from income/credit columns when needed.
    """
    df = _read_csv_any(path, max_rows)
    lower = {c.lower(): c for c in df.columns}
    label_col = lower.get("fraud_bool") or lower.get("isfraud") or lower.get("is_fraud")
    if label_col is None:
        raise ValueError("BAF adapter requires fraud_bool or an equivalent fraud label column.")
    amount_col = lower.get("amount")
    if amount_col is None:
        candidates = [lower.get(c) for c in ["income", "credit_risk_score", "proposed_credit_limit"] if lower.get(c)]
        if candidates:
            vals = pd.to_numeric(df[candidates[0]], errors="coerce").fillna(0).abs()
            df["_amount_proxy"] = (vals - vals.min() + 1) * 100
        else:
            df["_amount_proxy"] = 100.0
        amount_col = "_amount_proxy"
    out = _base_frame(df, "baf_public", amount_col, label_col,
                      account_col=lower.get("customer_age"), device_col=lower.get("device_os"), counterparty_col=lower.get("source"))
    if "device_os" in lower:
        out["channel"] = df[lower["device_os"]].astype(str).fillna("public_benchmark")
    out["source_file"] = str(Path(path).name)
    return out


def load_ieee_cis(transaction_path: str | Path, identity_path: str | Path | None = None, max_rows: int | None = None) -> pd.DataFrame:
    """Map IEEE-CIS transaction and optional identity files into canonical schema."""
    tx = _read_csv_any(transaction_path, max_rows)
    lower = {c.lower(): c for c in tx.columns}
    amount_col = lower.get("transactionamt") or lower.get("amount")
    label_col = lower.get("isfraud") or lower.get("is_fraud")
    if amount_col is None or label_col is None:
        raise ValueError("IEEE-CIS adapter requires TransactionAmt and isFraud columns.")
    if identity_path and Path(identity_path).exists():
        ident = _read_csv_any(identity_path, max_rows)
        if "TransactionID" in tx.columns and "TransactionID" in ident.columns:
            tx = tx.merge(ident, on="TransactionID", how="left", suffixes=("", "_id"))
            lower = {c.lower(): c for c in tx.columns}
    out = _base_frame(tx, "ieee_cis_public", amount_col, label_col,
                      event_id_col=lower.get("transactionid"), time_col=lower.get("transactiondt"),
                      account_col=lower.get("card1"), device_col=lower.get("deviceinfo"), counterparty_col=lower.get("addr1"))
    if lower.get("productcd"):
        out["payment_type"] = tx[lower["productcd"]].astype(str)
    out["source_file"] = str(Path(transaction_path).name)
    return out


def load_public_benchmarks_from_config(dataset_config: dict, max_rows: int | None = None) -> tuple[list[pd.DataFrame], dict]:
    paths = dataset_config.get("local_optional_paths", {}) if dataset_config else {}
    frames: list[pd.DataFrame] = []
    status: dict = {"loaded_sources": [], "skipped_sources": [], "max_rows_per_source": max_rows}
    specs = [
        ("paysim_public", paths.get("paysim_csv"), lambda p: load_paysim(p, max_rows)),
        ("baf_public", paths.get("baf_csv"), lambda p: load_baf(p, max_rows)),
        ("ieee_cis_public", paths.get("ieee_cis_transaction_csv"), lambda p: load_ieee_cis(p, paths.get("ieee_cis_identity_csv"), max_rows)),
    ]
    for name, path, loader in specs:
        if path and Path(path).exists():
            try:
                df = loader(path)
                frames.append(df)
                status["loaded_sources"].append({"source": name, "path": str(path), "rows": int(len(df))})
            except Exception as exc:
                status["skipped_sources"].append({"source": name, "path": str(path), "reason": str(exc)})
        else:
            status["skipped_sources"].append({"source": name, "path": str(path) if path else None, "reason": "not configured or not found"})
    return frames, status
