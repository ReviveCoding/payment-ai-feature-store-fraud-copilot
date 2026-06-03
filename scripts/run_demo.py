from __future__ import annotations
import argparse
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.config import DATA, OUTPUTS, REPORTS, MODELS, CONFIGS
from src.utils import read_yaml, write_json
from src.adapters.iso20022_adapter import load_iso20022_zip
from src.adapters.public_fraud_adapter import load_or_generate_public_fraud
from src.adapters.public_benchmark_adapters import load_public_benchmarks_from_config
from src.adapters.cfpb_adapter import load_or_generate_cfpb_sample
from src.adapters.canonical import combine_sources, validate_canonical
from src.spark_jobs.build_payment_features import build_features, spark_sql_style_validation
from src.feature_store.offline_store import write_partitioned_offline_store
from src.feature_store.online_lookup import build_online_store
from src.feature_store.point_in_time_join import build_training_set, validate_point_in_time
from src.feature_store.parity_checks import offline_online_parity
from src.modeling.train_models import train_vanilla_models, temporal_split
from src.specialty.residual_risk_correction import apply_residual_correction
from src.specialty.risk_envelope_pruning import apply_risk_envelope_pruning
from src.specialty.final_policy_selector import select_final_policy
from src.simulation.kpi_policy_simulator import simulate_policy_scenarios
from src.simulation.stress_testing import run_score_stress_tests
from src.sagemaker_pipeline.pipeline import build_sagemaker_compatible_pipeline_spec
from src.sagemaker_pipeline.register_model_step import register_local_model_package
from src.monitoring.release_gate import evaluate_release_gates
from src.monitoring.drift import drift_report
from src.monitoring.data_quality import evaluate_data_quality, evaluate_backfill_idempotence
from src.monitoring.model_monitoring_baseline import build_monitoring_baseline
from src.modeling.explainability import compute_feature_importance
from src.batch_scoring.score_batch import build_batch_scoring_sample
from src.rag_investigation.retrieve_evidence import retrieve_evidence
from src.rag_investigation.summarize_case import summarize_case
from src.nlp.transformer_text_routing import run_transformer_routing_smoke
from src.reporting import write_core_reports
from scripts.local_runnable_audit import run_audit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-mode", action="store_true", default=True)
    args = ap.parse_args()

    model_config = read_yaml(CONFIGS / "model_config.yaml")
    dataset_config = read_yaml(CONFIGS / "dataset_sources.yaml")
    gates = read_yaml(CONFIGS / "release_gates.yaml")
    n = int(model_config.get("sample_size", 2500))

    # 1. Load/generate data.
    public_frames, public_benchmark_status = load_public_benchmarks_from_config(dataset_config, max_rows=max(500, n // 2))
    if public_frames:
        # Keep generated public-style data as a stable baseline and add real user-supplied
        # public benchmark rows when local files are configured.
        fraud_df = pd.concat([load_or_generate_public_fraud(n=n), *public_frames], ignore_index=True)
    else:
        fraud_df = load_or_generate_public_fraud(n=n)
    iso_path = dataset_config.get("local_optional_paths", {}).get("iso20022_zip")
    iso_df = load_iso20022_zip(iso_path).head(max(0, n // 2)) if iso_path else pd.DataFrame()
    events = combine_sources([fraud_df, iso_df])
    schema_validation = validate_canonical(events)
    OUTPUTS.mkdir(exist_ok=True)
    events.to_csv(OUTPUTS / "canonical_payment_events.csv", index=False)

    # 2. Features / feature store.
    features = build_features(events)
    # Simulated rerun validates deterministic backfill/idempotence behavior.
    features_rerun = build_features(events)
    features.to_csv(OUTPUTS / "payment_features.csv", index=False)
    feature_validation = spark_sql_style_validation(features)
    offline_manifest = write_partitioned_offline_store(features, DATA / "feature_store_offline")
    online_meta = build_online_store(features, DATA / "online_store" / "online_features.sqlite")
    pit_validation = validate_point_in_time(features)
    parity = offline_online_parity(features, str(DATA / "online_store" / "online_features.sqlite"))
    data_quality = evaluate_data_quality(events, features, OUTPUTS)
    backfill_idempotence = evaluate_backfill_idempotence(features, features_rerun, OUTPUTS)

    # 3. Training and baselines.
    training_set = build_training_set(features)
    training_set.to_csv(OUTPUTS / "training_set_point_in_time.csv", index=False)
    train_result = train_vanilla_models(
        training_set,
        MODELS,
        test_fraction=float(model_config.get("temporal_test_fraction", 0.25)),
        capacity_fraction=float(model_config.get("review_capacity_fraction", 0.05)),
    )
    preds = pd.read_csv(train_result["test_predictions_path"], parse_dates=["event_time"])
    train_split = pd.read_csv(train_result["train_split_path"], parse_dates=["event_time"])
    test_split = pd.read_csv(train_result["test_split_path"], parse_dates=["event_time"])
    drift = drift_report(train_split, test_split, train_result["feature_names"][:8])

    # 4. Specialty improvements.
    preds, residual_metrics = apply_residual_correction(preds, capacity_fraction=float(model_config.get("review_capacity_fraction", 0.05)))
    preds, envelope_metrics = apply_risk_envelope_pruning(preds, capacity_fraction=float(model_config.get("review_capacity_fraction", 0.05)))
    preds, final_policy_metrics = select_final_policy(
        preds,
        ["score_operating_champion", "score_residual_corrected", "score_envelope_pruned"],
        capacity_fraction=float(model_config.get("review_capacity_fraction", 0.05)),
    )
    # Inherit latency proxy from the selected operating champion for local specialty policies.
    final_policy_metrics["p95_latency_ms_proxy"] = baseline_metrics_latency = train_result["results"].get(train_result["best_model_name"], {}).get("p95_latency_ms_proxy", 50)
    residual_metrics["p95_latency_ms_proxy"] = baseline_metrics_latency
    envelope_metrics["p95_latency_ms_proxy"] = baseline_metrics_latency
    preds.to_csv(OUTPUTS / "test_predictions_with_specialty.csv", index=False)
    stress_tests = run_score_stress_tests(preds, "score_final_operating_policy", capacity_fraction=float(model_config.get("review_capacity_fraction", 0.05)))
    explainability = compute_feature_importance(train_result["model_path"], test_split, OUTPUTS)
    monitoring_baseline = build_monitoring_baseline(train_split, preds, train_result["feature_names"], OUTPUTS)
    batch_scoring = build_batch_scoring_sample(preds, OUTPUTS / "batch_scoring_sample.csv")

    # 5. KPI simulator and release gates.
    kpi = simulate_policy_scenarios(preds, capacity_fraction=float(model_config.get("review_capacity_fraction", 0.05)))
    kpi.to_csv(OUTPUTS / "kpi_policy_scenarios.csv", index=False)
    final_metrics = final_policy_metrics
    baseline_metrics = train_result["results"].get(train_result["best_model_name"], {})
    release = evaluate_release_gates(final_metrics, baseline_metrics, gates)

    # 6. SageMaker-compatible artifacts.
    build_sagemaker_compatible_pipeline_spec(DATA / "model_registry" / "sagemaker_compatible_pipeline.json")
    approval = "Approved" if release["decision"] == "PASS" else "PendingManualApproval" if release["decision"] == "REVIEW" else "Rejected"
    register_local_model_package(
        DATA / "model_registry" / "model_package.json",
        train_result["model_path"],
        final_metrics,
        approval,
        train_result["feature_names"],
        governance_artifacts={
            "model_card": "reports/model_card.md",
            "validation_memo": "reports/validation_memo.md",
            "monitoring_baseline": "outputs/model_monitoring_baseline.json",
            "feature_importance": "outputs/feature_importance.csv",
            "batch_scoring_sample": "outputs/batch_scoring_sample.csv",
        },
    )

    # 7. RAG investigation sample.
    cfpb_path = dataset_config.get("local_optional_paths", {}).get("cfpb_csv")
    cfpb = load_or_generate_cfpb_sample(cfpb_path)
    cfpb.to_csv(DATA / "raw_sample" / "cfpb_style_narratives.csv", index=False)
    nlp_smoke = run_transformer_routing_smoke(cfpb, OUTPUTS / "nlp_routing_predictions.csv")
    top_cases = preds.sort_values("score_envelope_pruned", ascending=False).head(5)
    rag_samples = []
    for _, row in top_cases.iterrows():
        query = f"{row.get('fraud_type_proxy', '')} payment risk amount {row.get('amount')} rejected {row.get('rejected_flag')}"
        evidence = retrieve_evidence(query, cfpb, k=3)
        case = {"event_id": row["event_id"], "score": float(row["score_envelope_pruned"])}
        rag_samples.append({"case": case, "evidence": evidence, "investigation": summarize_case(case, evidence)})
    write_json(OUTPUTS / "rag_samples.json", rag_samples)

    # 8. Reports.
    artifacts = {
        "schema_validation": schema_validation,
        "public_benchmark_status": public_benchmark_status,
        "nlp_smoke": nlp_smoke,
        "feature_validation": feature_validation,
        "pit_validation": pit_validation,
        "parity": parity,
        "offline_manifest": offline_manifest,
        "online_meta": online_meta,
        "data_quality": data_quality,
        "backfill_idempotence": backfill_idempotence,
        "monitoring_baseline": monitoring_baseline,
        "explainability": explainability,
        "batch_scoring": batch_scoring,
        "model_results": train_result["results"],
        "model_selection": {"best_pr_auc_model_name": train_result.get("best_pr_auc_model_name"), "policy_model_name": train_result.get("policy_model_name"), "selected_operating_champion": train_result.get("best_model_name")},
        "drift": drift,
        "stress_tests": stress_tests,
        "specialty_metrics": {"residual_corrected": residual_metrics, "envelope_pruned": envelope_metrics, "final_operating_policy": final_policy_metrics},
        "kpi_scenarios": kpi,
        "release": release,
    }
    write_json(OUTPUTS / "run_artifacts.json", {k: v for k, v in artifacts.items() if not hasattr(v, "to_dict")})
    write_core_reports(ROOT, artifacts)
    audit = run_audit()
    print(json.dumps({"status": "ok", "rows": len(events), "feature_rows": len(features), "release_decision": release["decision"], "best_model": train_result["best_model_name"], "audit": audit["status"]}, indent=2))

if __name__ == "__main__":
    main()
