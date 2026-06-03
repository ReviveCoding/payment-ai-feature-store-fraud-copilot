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
