from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_generation.generate_sample_data import generate_public_style_fraud_sample, generate_cfpb_style_sample
from src.spark_jobs.build_payment_features import build_features
from src.feature_store.point_in_time_join import build_training_set
from src.specialty.residual_risk_correction import apply_residual_correction
from src.specialty.risk_envelope_pruning import apply_risk_envelope_pruning
from src.rag_investigation.retrieve_evidence import retrieve_evidence
from src.rag_investigation.summarize_case import summarize_case


def test_specialty_scores_exist():
    df = build_training_set(build_features(generate_public_style_fraud_sample(n=200, seed=5)))
    # Mimic prediction columns for unit testing specialty modules.
    preds = df.tail(60).copy()
    preds["score_calibrated"] = preds["rule_risk_prior"].clip(0, 1)
    preds["score_vanilla_best"] = (0.5 * preds["rule_risk_prior"] + 0.1).clip(0, 1)
    preds, m1 = apply_residual_correction(preds)
    preds, m2 = apply_risk_envelope_pruning(preds)
    assert "score_residual_corrected" in preds.columns
    assert "score_envelope_pruned" in preds.columns
    assert 0 <= m2["risk_region_f1_amount"] <= 1


def test_rag_guardrails():
    corpus = generate_cfpb_style_sample(n=10)
    evidence = retrieve_evidence("unauthorized fraud transfer", corpus, k=3)
    summary = summarize_case({"event_id": "x", "score": 0.9}, evidence)
    assert "summary" in summary
    assert "unsupported_claim_flag" in summary
