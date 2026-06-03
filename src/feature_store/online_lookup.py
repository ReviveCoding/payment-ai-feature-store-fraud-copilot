from __future__ import annotations
from pathlib import Path
import sqlite3
import pandas as pd

ONLINE_COLUMNS = [
    "event_id", "event_time", "account_id_hash", "amount", "rule_risk_prior", "txn_count_prior",
    "failed_txn_rate_prior", "new_device_flag", "new_beneficiary_flag", "high_risk_corridor_flag", "rejected_flag"
]


def build_online_store(features: pd.DataFrame, sqlite_path: str | Path) -> dict:
    sqlite_path = Path(sqlite_path)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    latest = features.sort_values("event_time").groupby("account_id_hash", as_index=False).tail(1)
    keep = [c for c in ONLINE_COLUMNS if c in latest.columns]
    conn = sqlite3.connect(sqlite_path)
    latest[keep].to_sql("latest_account_features", conn, if_exists="replace", index=False)
    conn.close()
    return {"sqlite_path": str(sqlite_path), "rows": int(len(latest)), "table": "latest_account_features"}


def lookup_account(sqlite_path: str | Path, account_id_hash: str) -> dict | None:
    conn = sqlite3.connect(sqlite_path)
    cur = conn.execute("select * from latest_account_features where account_id_hash = ?", (account_id_hash,))
    row = cur.fetchone()
    cols = [d[0] for d in cur.description]
    conn.close()
    return dict(zip(cols, row)) if row else None
