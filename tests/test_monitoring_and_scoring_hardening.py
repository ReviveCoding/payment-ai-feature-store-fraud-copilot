from pathlib import Path
import pandas as pd
from src.data_generation.generate_sample_data import generate_public_style_fraud_sample
from src.adapters.canonical import combine_sources
from src.spark_jobs.build_payment_features import build_features
from src.monitoring.data_quality import evaluate_data_quality, evaluate_backfill_idempotence
from src.monitoring.model_monitoring_baseline import build_monitoring_baseline
from src.batch_scoring.score_batch import build_batch_scoring_sample
from src.feature_store.point_in_time_join import build_training_set, MODEL_FEATURES


def test_data_quality_and_backfill_idempotence(tmp_path):
    events = combine_sources([generate_public_style_fraud_sample(n=120)])
    features = build_features(events)
    features2 = build_features(events)
    dq = evaluate_data_quality(events, features, tmp_path)
    backfill = evaluate_backfill_idempotence(features, features2, tmp_path)
    assert dq["status"] == "PASS"
    assert backfill["status"] == "PASS"
    assert (tmp_path / "data_quality_baseline.json").exists()
    assert (tmp_path / "backfill_idempotence.json").exists()


def test_monitoring_baseline_and_batch_scoring(tmp_path):
    events = combine_sources([generate_public_style_fraud_sample(n=140)])
    features = build_features(events)
    training = build_training_set(features)
    train = training.iloc[:90].copy()
    preds = training.iloc[90:].copy()
    preds["score_final_operating_policy"] = preds["rule_risk_prior"].clip(0, 1)
    baseline = build_monitoring_baseline(train, preds, MODEL_FEATURES, tmp_path)
    scoring = build_batch_scoring_sample(preds, tmp_path / "batch_scoring_sample.csv", n=15)
    assert baseline["status"] == "PASS"
    assert "feature_constraints" in baseline
    assert scoring["status"] == "PASS"
    assert scoring["rows_scored"] == 15
    assert (tmp_path / "batch_scoring_sample.csv").exists()
