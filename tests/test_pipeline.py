from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_generation.generate_sample_data import generate_public_style_fraud_sample
from src.adapters.canonical import combine_sources, validate_canonical
from src.spark_jobs.build_payment_features import build_features
from src.feature_store.point_in_time_join import validate_point_in_time, build_training_set
from src.modeling.metrics import evaluate_scores


def test_canonical_schema_validates():
    df = generate_public_style_fraud_sample(n=200, seed=1)
    canonical = combine_sources([df])
    result = validate_canonical(canonical)
    assert result["valid"] is True
    assert result["rows"] == 200


def test_point_in_time_features_are_prior_only():
    df = generate_public_style_fraud_sample(n=300, seed=2)
    features = build_features(df)
    result = validate_point_in_time(features)
    assert result["point_in_time_valid"] is True


def test_training_set_and_metrics():
    df = generate_public_style_fraud_sample(n=300, seed=3)
    features = build_features(df)
    ts = build_training_set(features)
    assert "risk_label" in ts.columns
    y = ts["risk_label"].values
    scores = ts["rule_risk_prior"].values
    metrics = evaluate_scores(y, scores, ts["amount"].values, 0.05)
    assert 0 <= metrics["pr_auc"] <= 1
    assert 0 <= metrics["ece"] <= 1
