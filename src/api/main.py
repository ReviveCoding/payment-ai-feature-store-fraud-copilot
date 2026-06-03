from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Payment Fraud-Risk Scoring API", version="1.0-local")

class PaymentRiskRequest(BaseModel):
    amount: float
    rule_risk_prior: float = 0.0
    new_device_flag: int = 0
    new_beneficiary_flag: int = 0
    high_risk_corridor_flag: int = 0

@app.get("/health")
def health():
    return {"status": "ok", "claim_boundary": "local demo API, not production deployment"}

@app.post("/score")
def score(req: PaymentRiskRequest):
    heuristic = min(1.0, 0.15 + 0.0001 * req.amount + 0.55 * req.rule_risk_prior + 0.05 * req.new_device_flag + 0.05 * req.new_beneficiary_flag + 0.10 * req.high_risk_corridor_flag)
    action = "block_or_escalate" if heuristic >= 0.85 else "human_review" if heuristic >= 0.45 else "approve"
    return {"score": heuristic, "recommended_action": action}
