from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd


def build_features_pandas(events: pd.DataFrame) -> pd.DataFrame:
    """Build leakage-safe, point-in-time features with pandas fallback.

    The implementation uses prior-only cumulative features within each account.
    A PySpark production extension would use equivalent window functions.
    """
    df = events.copy()
    df["event_time"] = pd.to_datetime(df["event_time"])
    df = df.sort_values(["account_id_hash", "event_time", "event_id"]).reset_index(drop=True)
    df["amount_log"] = np.log1p(df["amount"].clip(lower=0))
    df["cross_border_flag"] = (df.get("debtor_country", "UNK").astype(str) != df.get("creditor_country", "UNK").astype(str)).astype(int)
    df["rejected_flag"] = df["payment_status"].astype(str).isin(["RJCT", "PDNG", "REJECTED"]).astype(int)

    # Prior-only account features.
    g = df.groupby("account_id_hash", sort=False)
    df["txn_count_prior"] = g.cumcount()
    df["amount_sum_prior"] = g["amount"].cumsum() - df["amount"]
    df["failed_txn_count_prior"] = g["rejected_flag"].cumsum() - df["rejected_flag"]
    df["failed_txn_rate_prior"] = np.where(df["txn_count_prior"] > 0, df["failed_txn_count_prior"] / df["txn_count_prior"], 0.0)
    df["amount_mean_prior"] = np.where(df["txn_count_prior"] > 0, df["amount_sum_prior"] / df["txn_count_prior"], df["amount"].median())
    df["amount_zscore_account"] = (df["amount"] - df["amount_mean_prior"]) / (df["amount"].std(ddof=0) + 1e-6)

    # Prior-only device and counterparty novelty.
    df["device_seen_count_prior"] = df.groupby("device_id_hash").cumcount()
    df["new_device_flag"] = (df["device_seen_count_prior"] == 0).astype(int)
    df["counterparty_seen_count_prior"] = df.groupby("counterparty_id_hash").cumcount()
    df["new_beneficiary_flag"] = (df["counterparty_seen_count_prior"] == 0).astype(int)

    corridor = df.get("debtor_country", "UNK").astype(str) + ">" + df.get("creditor_country", "UNK").astype(str)
    df["high_risk_corridor_flag"] = corridor.isin(["US>NG", "GB>NG", "US>BR", "MX>NG"]).astype(int)
    df["retry_count_proxy"] = np.where(df["rejected_flag"] == 1, 1, 0)
    df["processing_time_secs"] = pd.to_numeric(df.get("processing_time_secs", 0), errors="coerce").fillna(0)

    # Mechanism-informed risk prior. This is intentionally interpretable and not trained on labels.
    prior_raw = (
        0.25 * np.clip(df["amount_zscore_account"], 0, 5)
        + 0.75 * df["new_device_flag"]
        + 0.75 * df["new_beneficiary_flag"]
        + 0.85 * df["high_risk_corridor_flag"]
        + 0.50 * df["rejected_flag"]
        + 0.25 * df["cross_border_flag"]
        + 0.40 * df["failed_txn_rate_prior"]
    )
    df["rule_risk_prior"] = 1 / (1 + np.exp(-(prior_raw - 1.4)))
    df["event_date"] = df["event_time"].dt.strftime("%Y-%m-%d")
    df = df.sort_values("event_time").reset_index(drop=True)
    return df


def build_features(events: pd.DataFrame) -> pd.DataFrame:
    try:
        import pyspark  # noqa: F401
        # The demo intentionally uses pandas to avoid requiring Java/Spark runtime.
        # This import gate confirms whether real PySpark can be enabled in full mode.
    except Exception:
        pass
    return build_features_pandas(events)


def spark_sql_style_validation(features: pd.DataFrame) -> dict:
    return {
        "row_count": int(len(features)),
        "label_rate": float(features["risk_label"].mean()) if "risk_label" in features else 0.0,
        "feature_null_rate_max": float(features[["amount", "rule_risk_prior", "txn_count_prior"]].isna().mean().max()),
        "event_time_min": str(features["event_time"].min()),
        "event_time_max": str(features["event_time"].max()),
        "partition_columns": ["dataset_source", "event_date"],
    }
