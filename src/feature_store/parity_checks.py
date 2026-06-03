from __future__ import annotations
import pandas as pd
import sqlite3


def offline_online_parity(features: pd.DataFrame, sqlite_path: str) -> dict:
    latest_offline = features.sort_values("event_time").groupby("account_id_hash", as_index=False).tail(1)
    conn = sqlite3.connect(sqlite_path)
    latest_online = pd.read_sql_query("select account_id_hash, event_id, rule_risk_prior from latest_account_features", conn)
    conn.close()
    merged = latest_offline[["account_id_hash", "event_id", "rule_risk_prior"]].merge(latest_online, on="account_id_hash", suffixes=("_offline", "_online"))
    event_match = (merged["event_id_offline"] == merged["event_id_online"]).mean() if len(merged) else 0
    score_diff = (merged["rule_risk_prior_offline"] - merged["rule_risk_prior_online"]).abs().max() if len(merged) else 0
    return {"matched_accounts": int(len(merged)), "event_match_rate": float(event_match), "max_rule_prior_diff": float(score_diff), "parity_pass": bool(event_match == 1.0 and score_diff < 1e-9)}
