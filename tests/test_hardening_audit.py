from __future__ import annotations
import pandas as pd
from scripts.local_runnable_audit import run_audit
from src.simulation.stress_testing import run_score_stress_tests


def test_local_runnable_audit_pass_or_review():
    result = run_audit()
    assert result["status"] in {"PASS", "REVIEW"}
    assert result["claim_boundary_present"] is True


def test_stress_testing_outputs_metrics():
    df = pd.DataFrame({
        "risk_label": [0, 1, 0, 1, 0, 1],
        "amount": [10, 200, 20, 300, 50, 100],
        "score_envelope_pruned": [0.1, 0.9, 0.2, 0.8, 0.3, 0.7],
        "score_residual_corrected": [0.1, 0.85, 0.2, 0.75, 0.3, 0.65],
    })
    out = run_score_stress_tests(df, capacity_fraction=0.33)
    assert "base" in out and "amount_shock" in out
    assert "fraud_loss_capture_rate" in out["base"]
