from __future__ import annotations
import pandas as pd
from src.specialty.final_policy_selector import select_final_policy


def test_final_policy_selector_chooses_available_candidate():
    df = pd.DataFrame({
        "risk_label": [0, 1, 0, 1, 0, 1, 0, 1],
        "amount": [10, 200, 20, 300, 40, 100, 50, 250],
        "score_a": [0.1, 0.9, 0.2, 0.8, 0.1, 0.7, 0.2, 0.9],
        "score_b": [0.5] * 8,
    })
    out, metrics = select_final_policy(df, ["score_a", "score_b"], capacity_fraction=0.25)
    assert "score_final_operating_policy" in out.columns
    assert metrics["selected_policy_name"] in {"a", "b"}
