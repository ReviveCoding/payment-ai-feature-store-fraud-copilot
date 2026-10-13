# Payment AI Feature Store & Fraud-Risk Intelligence Platform

**Subtitle:** Evidence-grounded GenAI investigation and Risk/Compliance validation for payment fraud-risk ML.

This project is a **local-runnable, AWS-patterned, production-style reference framework** for offline fraud-risk investigation and model evaluation. It demonstrates a payment fraud-risk ML lifecycle:

```text
public/proxy fraud data + synthetic ISO 20022 pacs.008/pacs.002
→ canonical payment-event schema
→ PySpark-compatible ETL and Spark-SQL-style validation
→ point-in-time offline/online feature-store artifacts
→ vanilla fraud baselines
→ calibrated approve/review/block decision policy
→ reliability specialty upgrades
→ SageMaker-compatible pipeline and model registry artifacts
→ model card, validation memo, control matrix, release decision
→ optional CFPB-style evidence-grounded GenAI investigation
```

## Why this project exists

The project is designed to show core skills for applied AI/ML in payments:

- payment-domain feature engineering
- fraud-risk modeling with class imbalance and review-capacity constraints
- PySpark/EMR-compatible batch feature processing
- offline/online feature-store fundamentals
- leakage-safe point-in-time training sets
- SageMaker-style model lifecycle and approval artifacts
- Risk/Compliance-ready validation documentation
- evidence-grounded GenAI investigation as a supporting layer, not the core decision engine

## Claim boundaries

This project **does not** use proprietary bank data, JPMorgan Chase data, real customer data, or production payment data. It uses small generated/public-style samples and, when available locally, synthetic ISO 20022 payment data. AWS artifacts are local, AWS-patterned, EMR-compatible, and SageMaker-compatible unless explicitly run on AWS.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
make run-demo
make test
make reports
make audit
# Optional full local verification from a clean generated-artifact state
make verify
```

The default demo runs without external downloads, Kaggle credentials, AWS credentials, or proprietary data.

## Core reports

After `make run-demo`, review:

- `reports/feature_store_validation_report.md`
- `reports/baseline_vs_specialty_ablation_report.md`
- `reports/validation_memo.md`
- `reports/kpi_policy_readout.md`
- `reports/release_decision.md`
- `reports/public_dataset_extension_report.md`
- `reports/transformer_finetuning_smoke_report.md`
- `reports/deployment_readiness.md`
- `reports/data_quality_and_backfill_report.md`
- `reports/model_monitoring_baseline_report.md`
- `reports/explainability_report.md`
- `reports/batch_scoring_contract_report.md`

## Repository structure

```text
src/adapters/              dataset adapters and canonical schema mapping
src/spark_jobs/            PySpark-compatible ETL with pandas fallback
src/feature_store/         offline/online feature store, PIT joins, parity checks
src/modeling/              vanilla baselines, calibration, model evaluation
src/specialty/             residual correction, risk envelope pruning, optional PBHT
src/simulation/            KPI-based decision policy simulator
src/rag_investigation/     evidence retrieval, case summary, guardrails
src/sagemaker_pipeline/    SageMaker-compatible pipeline and model registry templates
reports/                   generated evidence artifacts
```

## One-command outputs

`make run-demo` builds sample data, features, models, specialty comparisons, registry metadata, RAG samples, and validation reports.


## Docker / Kubernetes readiness

This repository now includes `Dockerfile`, `docker-compose.yml`, and Kubernetes scaffolding under `k8s/`. These artifacts are intended to demonstrate deployment readiness only. They do not imply production deployment or cloud execution.

## Public benchmark extension

Configure optional public benchmark paths in `configs/dataset_sources.yaml` to run against user-supplied PaySim, Bank Account Fraud Dataset Suite, or IEEE-CIS files. The default `make run-demo` remains external-download-free and uses generated public-style fraud samples when those files are absent.


## Validation and operational checks

- Champion/challenger operating-model selection using fraud-review utility, not PR-AUC alone.
- Drift monitoring report using temporal train/test PSI checks.
- Small-data stress tests for amount shock, score-compression drift, and envelope-pruning contribution.
- Local/GitHub runnable audit with required-file, claim-boundary, large-file, and secret-like-file checks.
- Data-quality baseline and deterministic backfill idempotence validation.
- Model-Monitor-style baseline, local explainability diagnostics, and offline batch scoring contract.
- GitHub Actions workflow scaffold under `.github/workflows/local-ci.yml`, plus `pyproject.toml` for Python project metadata and pytest configuration.

For additional implementation details, see `PROJECT_MANIFEST.md` and the evaluation reports in `reports/`.
