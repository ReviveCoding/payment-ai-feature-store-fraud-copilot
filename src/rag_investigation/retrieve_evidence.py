from __future__ import annotations
import re
import pandas as pd


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z]{3,}", str(text).lower()))


def retrieve_evidence(query: str, corpus: pd.DataFrame, k: int = 3) -> list[dict]:
    q = _tokens(query)
    rows = []
    for _, row in corpus.iterrows():
        doc = row.get("narrative", "")
        d = _tokens(doc)
        score = len(q & d) / max(1, len(q | d))
        rows.append({"score": score, "complaint_id": row.get("complaint_id", "unknown"), "narrative": doc, "product": row.get("product", "unknown"), "issue": row.get("issue", "unknown")})
    return sorted(rows, key=lambda r: r["score"], reverse=True)[:k]
