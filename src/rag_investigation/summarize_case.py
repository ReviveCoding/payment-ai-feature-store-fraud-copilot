from __future__ import annotations
from src.rag_investigation.guardrails import check_evidence_support, detect_source_conflict


def summarize_case(case: dict, evidence: list[dict]) -> dict:
    support = check_evidence_support(evidence)
    conflict = detect_source_conflict(evidence)
    if support["abstain"]:
        summary = "Insufficient evidence for an automated investigation summary. Route to human review."
    else:
        top = evidence[0]
        summary = (
            f"Payment case {case.get('event_id')} has risk score {case.get('score', 0):.3f}. "
            f"Top supporting evidence relates to {top.get('issue')} for {top.get('product')}. "
            f"Recommended action: human review if score remains above the configured review threshold."
        )
    return {"summary": summary, **support, **conflict}
