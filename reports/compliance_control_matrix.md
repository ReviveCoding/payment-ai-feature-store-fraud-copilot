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
