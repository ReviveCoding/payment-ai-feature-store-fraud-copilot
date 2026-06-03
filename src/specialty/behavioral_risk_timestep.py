from __future__ import annotations
import pandas as pd


def add_behavioral_risk_timestep(features: pd.DataFrame) -> pd.DataFrame:
    """Optional/default-off PHT-inspired behavioral risk timestep.

    This conservative implementation does not train a sequence model. It creates a transparent
    behavior-adjusted risk age from prior activity and risk-prior jumps. Enable only when the
    underlying dataset has meaningful account-level sequences.
    """
    df = features.sort_values(["account_id_hash", "event_time"]).copy()
    df["pbht_proxy"] = df["txn_count_prior"] + 5 * df["rule_risk_prior"] + 2 * df["failed_txn_rate_prior"]
    df["pbht_jump"] = df.groupby("account_id_hash")["pbht_proxy"].diff().fillna(0).clip(lower=0)
    return df
