from __future__ import annotations


def check_evidence_support(evidence: list[dict], min_score: float = 0.05) -> dict:
    best = evidence[0]["score"] if evidence else 0.0
    unsupported = best < min_score
    return {
        "best_evidence_score": float(best),
        "unsupported_claim_flag": bool(unsupported),
        "abstain": bool(unsupported),
    }


def detect_source_conflict(evidence: list[dict]) -> dict:
    statuses = set()
    for e in evidence:
        text = str(e.get("narrative", "")).lower()
        if "unauthorized" in text or "fraud" in text:
            statuses.add("risk_signal")
        if "delay" in text or "fee" in text:
            statuses.add("operations_signal")
    return {"source_conflict_flag": len(statuses) > 1, "signal_types": sorted(statuses)}
