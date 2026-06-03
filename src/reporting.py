from __future__ import annotations
from pathlib import Path
import json
import pandas as pd


def md_table(df: pd.DataFrame, float_fmt: str = ".4f") -> str:
    """Render a markdown table without requiring optional pandas tabulate dependency.

    Pandas `DataFrame.to_markdown` depends on the optional `tabulate` package.
    GitHub/local smoke runs should work from the minimal requirements file, so this
    helper falls back to a small built-in markdown renderer if tabulate is absent.
    """
    if df.empty:
        return "No rows."
    try:
        return df.to_markdown(index=False, floatfmt=float_fmt)
    except ImportError:
        work = df.copy()
        for col in work.columns:
            work[col] = work[col].map(lambda v: format(v, float_fmt) if isinstance(v, float) else ("" if pd.isna(v) else str(v)))
        headers = [str(c) for c in work.columns]
        rows = work.astype(str).values.tolist()
        out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
        out.extend("| " + " | ".join(row) + " |" for row in rows)
        return "\n".join(out)


def write_core_reports(root: Path, artifacts: dict) -> None:
    reports = root / "reports"
    outputs = root / "outputs"
    reports.mkdir(exist_ok=True)

    validation = artifacts.get("schema_validation", {})
    feature_validation = artifacts.get("feature_validation", {})
    pit = artifacts.get("pit_validation", {})
    parity = artifacts.get("parity", {})
    manifest = artifacts.get("offline_manifest", {})
    (reports / "feature_store_validation_report.md").write_text(f"""
# Feature Store Validation Report

## Schema validation

```json
{json.dumps(validation, indent=2)}
```

## Spark-SQL-style feature validation

```json
{json.dumps(feature_validation, indent=2)}
```

## Point-in-time validation

```json
{json.dumps(pit, indent=2)}
```

## Offline/online parity

```json
{json.dumps(parity, indent=2)}
```

## Offline store manifest

- Format: `{manifest.get('format')}`
- Rows: `{manifest.get('rows')}`
- Partitions: `{len(manifest.get('partitions', []))}`

Note: the demo writes Parquet when a Parquet engine is installed; otherwise it writes a CSV fallback while preserving partitioning and manifest metadata.
""".strip() + "\n", encoding="utf-8")



    data_quality = artifacts.get("data_quality", {})
    backfill_idempotence = artifacts.get("backfill_idempotence", {})
    (reports / "data_quality_and_backfill_report.md").write_text(f"""
# Data Quality and Backfill Idempotence Report

## Data quality baseline

```json
{json.dumps(data_quality, indent=2)}
```

## Backfill idempotence

```json
{json.dumps(backfill_idempotence, indent=2)}
```

## Interpretation

This report hardens the feature pipeline beyond simple row-count checks. It verifies required columns, null rates, duplicate event IDs, amount sanity, source coverage, and deterministic feature hashes for repeatable batch backfills.
""".strip() + "\n", encoding="utf-8")

    public_status = artifacts.get("public_benchmark_status", {})
    (reports / "public_dataset_extension_report.md").write_text(f"""
# Public Dataset Extension Report

This project is runnable without external downloads, but it includes dataset-specific adapters for user-supplied public fraud benchmarks.

```json
{json.dumps(public_status, indent=2)}
```

## Supported adapter paths

- PaySim-style CSV: `configs/dataset_sources.yaml -> local_optional_paths.paysim_csv`
- Bank Account Fraud Dataset Suite CSV: `configs/dataset_sources.yaml -> local_optional_paths.baf_csv`
- IEEE-CIS transaction CSV: `configs/dataset_sources.yaml -> local_optional_paths.ieee_cis_transaction_csv`
- IEEE-CIS identity CSV: `configs/dataset_sources.yaml -> local_optional_paths.ieee_cis_identity_csv`

If these files are not present, `make run-demo` uses generated public-style payment-fraud samples so that the engineering, feature-store, and validation pipeline remains reproducible.
""".strip() + "\n", encoding="utf-8")

    nlp = artifacts.get("nlp_smoke", {})
    (reports / "transformer_finetuning_smoke_report.md").write_text(f"""
# Transformer / NLP Routing Smoke Report

This report addresses the JD signal around NLP, LLMs, Transformers, and fine-tuning while keeping the core project centered on payment fraud-risk feature stores.

```json
{json.dumps(nlp, indent=2)}
```

## Interpretation

The default run is offline-safe. If the `transformers` package and local model weights are available, this module can be extended to DistilBERT/MiniLM-style fine-tuning for complaint issue or risk routing. Without local model weights, the project runs a TF-IDF logistic fallback and explicitly avoids claiming real Transformer fine-tuning.
""".strip() + "\n", encoding="utf-8")

    (reports / "deployment_readiness.md").write_text("""
# Deployment Readiness Report

## Included artifacts

- `Dockerfile` for containerized local scoring/report generation.
- `docker-compose.yml` for local API execution.
- `k8s/deployment.yaml` and `k8s/service.yaml` for Kubernetes-ready scaffolding.
- `reports/emr_sagemaker_optional_runbook.md` for optional AWS validation.

## Claim boundary

These artifacts demonstrate deployment readiness and platform awareness. They do not prove production deployment, enterprise security approval, on-call ownership, or actual AWS execution unless those runs are performed and logged separately.
""".strip() + "\n", encoding="utf-8")

    model_results = artifacts.get("model_results", {})
    specialty = artifacts.get("specialty_metrics", {})
    rows = []
    for name, metrics in model_results.items():
        row = {"model": name}
        row.update({k: metrics.get(k) for k in ["pr_auc", "roc_auc", "precision_at_capacity", "recall_at_capacity", "fraud_loss_capture_rate", "brier", "ece", "p95_latency_ms_proxy"]})
        rows.append(row)
    for name, metrics in specialty.items():
        row = {"model": name}
        row.update({k: metrics.get(k) for k in ["pr_auc", "roc_auc", "precision_at_capacity", "recall_at_capacity", "fraud_loss_capture_rate", "brier", "ece", "p95_latency_ms_proxy", "risk_region_f1_amount"]})
        rows.append(row)
    ablation = pd.DataFrame(rows)
    (reports / "baseline_vs_specialty_ablation_report.md").write_text(f"""
# Baseline vs Specialty Ablation Report

This report compares vanilla fraud-risk baselines against specialty reliability upgrades.

{md_table(ablation)}

## Interpretation

The project treats improvements broadly: PR-AUC, Precision@review capacity, fraud-loss capture, calibration, and review-burden tradeoffs are all decision-relevant. The final release decision is made through the KPI simulator and release gates rather than a single AUC metric.
""".strip() + "\n", encoding="utf-8")


    # Model selection report: separates PR-AUC champion from operating champion.
    selection = artifacts.get("model_selection", {})
    (reports / "model_selection_report.md").write_text(f"""
# Model Selection Report

This project separates statistical ranking performance from operating-policy usefulness.

```json
{json.dumps(selection, indent=2)}
```

- `best_pr_auc_model_name` is the model with the strongest PR-AUC.
- `policy_model_name` is selected using a fraud-operations utility that balances PR-AUC, Precision@review capacity, fraud-loss capture, and calibration.
- `selected_operating_champion` is the score source used by downstream residual correction and risk-envelope pruning.
""".strip() + "\n", encoding="utf-8")

    drift = artifacts.get("drift", {})
    (reports / "drift_monitoring_report.md").write_text(f"""
# Drift Monitoring Report

Population Stability Index (PSI) is calculated on the temporal train/test split for core feature-store columns.

```json
{json.dumps(drift, indent=2)}
```

Interpretation guide: PSI below 0.10 is usually treated as low shift, 0.10-0.25 as moderate review, and above 0.25 as high shift requiring investigation. These thresholds are heuristic and should be replaced by organization-specific standards in production.
""".strip() + "\n", encoding="utf-8")

    stress = artifacts.get("stress_tests", {})
    (reports / "stress_test_report.md").write_text(f"""
# Small-Data Stress Test Report

These checks validate score behavior on local/synthetic data before any full public benchmark or cloud run.

```json
{json.dumps(stress, indent=2)}
```

The stress tests are not production validation. They are intended to show that the framework includes robustness checks for payment amount shocks, score compression drift, and envelope-pruning contribution.
""".strip() + "\n", encoding="utf-8")

    (reports / "hardening_loop_report.md").write_text("""
# Hardening Loop Report

## Loop 1: Operating-model selection

Weakness: the earlier version selected a model mainly by PR-AUC, which can underrepresent fraud-review operations.

Improvement: added a champion/challenger selection rule that balances PR-AUC, Precision@review capacity, fraud-loss capture, and calibration. Downstream specialty modules now start from the operating champion.

## Loop 2: Reliability and drift evidence

Weakness: drift and robustness checks existed conceptually but were not first-class generated evidence.

Improvement: added temporal PSI drift monitoring and small-data stress tests for amount shocks, score compression drift, and envelope-pruning contribution.

## Loop 3: Data quality, backfill, and monitoring hardening

Weakness: the previous version validated point-in-time features and parity, but it did not create a first-class data-quality baseline or idempotent backfill evidence.

Improvement: added `reports/data_quality_and_backfill_report.md`, `outputs/data_quality_baseline.json`, and `outputs/backfill_idempotence.json` to verify null rates, duplicates, source coverage, amount sanity, and deterministic reruns.

## Loop 4: Explainability and batch-scoring contract

Weakness: the model registry recorded metrics and lineage, but model-review evidence was still thin around feature attribution and downstream scoring contracts.

Improvement: added local permutation-importance diagnostics, a Model-Monitor-style baseline, and a batch scoring sample with approve/review/escalate decision mapping.

## Loop 5: Local/GitHub runnable hygiene

Weakness: runnable claims needed an explicit audit artifact.

Improvement: added `scripts/local_runnable_audit.py`, `reports/local_github_runnable_audit.md`, and GitHub Actions workflow scaffolding.

## Stop condition

Remaining improvements are either environment-dependent, such as actual AWS EMR/SageMaker execution, or data-dependent, such as full public benchmark runs. Further changes without those external resources would be minor relative to the current local-runnable scope.
""".strip() + "\n", encoding="utf-8")


    monitoring_baseline = artifacts.get("monitoring_baseline", {})
    (reports / "model_monitoring_baseline_report.md").write_text(f"""
# Model Monitoring Baseline Report

```json
{json.dumps(monitoring_baseline, indent=2)}
```

This local artifact mirrors a production monitoring baseline: feature distribution statistics, constraints, and score distribution summaries. It is not an active SageMaker Model Monitor schedule unless deployed on AWS.
""".strip() + "\n", encoding="utf-8")

    explainability = artifacts.get("explainability", {})
    top_features = pd.DataFrame(explainability.get("top_features", []))
    explainability_table = md_table(top_features) if not top_features.empty else "No explainability rows."
    (reports / "explainability_report.md").write_text(f"""
# Explainability Report

## Summary

```json
{json.dumps({k: v for k, v in explainability.items() if k != 'top_features'}, indent=2)}
```

## Top local feature attribution diagnostics

{explainability_table}

This report provides local permutation-importance diagnostics for the operating champion. It is intended for model-review discussion, not as a substitute for enterprise-approved explainability tooling.
""".strip() + "\n", encoding="utf-8")

    batch_scoring = artifacts.get("batch_scoring", {})
    (reports / "batch_scoring_contract_report.md").write_text(f"""
# Batch Scoring Contract Report

```json
{json.dumps(batch_scoring, indent=2)}
```

The generated batch scoring sample documents the score column, decision mapping, decision counts, and human-review routing output. It is an offline contract artifact, not a production decision service.
""".strip() + "\n", encoding="utf-8")

    kpi = artifacts.get("kpi_scenarios")
    kpi_text = md_table(kpi) if isinstance(kpi, pd.DataFrame) else "No KPI scenarios generated."
    (reports / "kpi_policy_readout.md").write_text(f"""
# KPI Policy Readout

Policy scenarios compare fraud capture, review capacity, calibration, and decision score.

{kpi_text}
""".strip() + "\n", encoding="utf-8")

    release = artifacts.get("release", {})
    (reports / "release_decision.md").write_text(f"""
# Release Decision

Decision: **{release.get('decision', 'UNKNOWN')}**

```json
{json.dumps(release, indent=2)}
```

This decision is for the local reference framework only. It is not a production approval.
""".strip() + "\n", encoding="utf-8")

    (reports / "validation_memo.md").write_text(f"""
# Validation Memo

## Objective

Validate a local-runnable payment fraud-risk ML lifecycle using public-style/synthetic data, point-in-time feature engineering, model calibration, review-capacity metrics, and governance artifacts.

## Scope boundaries

- No proprietary bank data.
- No JPMorgan Chase data.
- No production deployment.
- AWS components are local compatible templates unless explicitly executed on AWS.

## Key controls

| Risk | Control | Evidence |
|---|---|---|
| Future leakage | Point-in-time feature test | `reports/feature_store_validation_report.md` |
| Feature inconsistency | Offline/online parity check | `reports/feature_store_validation_report.md` |
| Poor calibration | ECE and Brier score | `reports/baseline_vs_specialty_ablation_report.md` |
| Data-quality instability | Null/duplicate/source/amount checks | `reports/data_quality_and_backfill_report.md` |
| Monitoring readiness | Local constraints and score baseline | `reports/model_monitoring_baseline_report.md` |
| Model explainability | Permutation-importance diagnostics | `reports/explainability_report.md` |
| Excess review burden | Review-capacity KPI simulator | `reports/kpi_policy_readout.md` |
| Unsupported GenAI claims | Evidence support and abstention checks | RAG outputs in `outputs/rag_samples.json` |
| Overclaiming | Claim boundary file | `CLAIM_BOUNDARIES.md` |

## Recommendation

Use this project as an interview and portfolio reference framework. Do not represent it as a deployed production fraud system.
""".strip() + "\n", encoding="utf-8")

    (reports / "model_card.md").write_text(f"""
# Model Card: Payment Fraud-Risk Classifier

## Intended use

Offline evaluation of fraud-risk ranking and review-routing policies on public-style/synthetic payment data.

## Not intended for

Production fraud decisions, real customer decisions, or regulatory approval.

## Data

Generated public-style fraud data and synthetic ISO 20022 payment events when available locally.

## Metrics

See `baseline_vs_specialty_ablation_report.md` and `kpi_policy_readout.md`.

## Limitations

Public/proxy/synthetic data cannot fully represent proprietary payment networks, customer behavior, fraud operations, or production model risk constraints.
""".strip() + "\n", encoding="utf-8")

    (reports / "compliance_control_matrix.md").write_text("""
# Compliance Control Matrix

| Risk | Control | Evidence artifact | Status |
|---|---|---|---|
| Data leakage | Point-in-time join validation | feature_store_validation_report.md | PASS if PIT flag true |
| Feature inconsistency | Offline/online parity | feature_store_validation_report.md | PASS if parity flag true |
| Poor calibration | ECE / Brier | ablation report | REVIEW if ECE high |
| Excess false positives | Review burden and Precision@K | KPI readout | REVIEW |
| Unsupported GenAI output | Evidence support check | rag samples | PASS/REVIEW |
| Model monitoring gaps | Data-quality and score-distribution baseline | model_monitoring_baseline_report.md | PASS/REVIEW |
| Explainability gaps | Local feature importance | explainability_report.md | PASS/REVIEW |
| Batch scoring contract gaps | Offline batch scoring sample | batch_scoring_contract_report.md | PASS |
| Cloud overclaim | Claim boundary file | CLAIM_BOUNDARIES.md | PASS |
""".strip() + "\n", encoding="utf-8")

    (reports / "stakeholder_summary.md").write_text(f"""
# Stakeholder Summary

The recommended policy is based on the highest KPI decision score and release-gate outcome. The framework prioritizes fraud-loss capture, calibration, review burden, and operational transparency over a single aggregate accuracy metric.

See `release_decision.md` for the final local reference decision.
""".strip() + "\n", encoding="utf-8")

    (reports / "architecture.md").write_text("""
# Architecture

```text
Data adapters
→ canonical payment schema
→ PySpark-compatible feature processing
→ offline/online feature store
→ point-in-time training set
→ vanilla models
→ calibration and threshold policy
→ specialty reliability upgrades
→ model registry
→ RAG investigation for high-risk cases
→ validation reports and release gates
```
""".strip() + "\n", encoding="utf-8")

    (reports / "data_card.md").write_text("""
# Data Card

The default demo uses generated public-style payment fraud samples, generated CFPB-style narratives, and optional local synthetic ISO 20022 files. This data is suitable for demonstrating engineering, modeling, and governance workflows, but not for production fraud validation.
""".strip() + "\n", encoding="utf-8")

    (reports / "leakage_risk_report.md").write_text("""
# Leakage Risk Report

Controls included:

- temporal split for evaluation
- prior-only cumulative account features
- point-in-time validation where `txn_count_prior` equals prior account events
- status features are synthetic/proxy and documented
- no post-review production labels are used
""".strip() + "\n", encoding="utf-8")
