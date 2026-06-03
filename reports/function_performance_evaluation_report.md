# Function and Performance Evaluation Report

## Summary

- Status: **PASS**
- core_reports_present: 10/10
- model_registry_present: True
- release_decision_detected: True
- ablation_metrics_detected: True
- feature_store_validation_detected: True
- data_quality_checks_detected: True

## Core Report Availability

- feature_store_validation_report.md: PASS
- baseline_vs_specialty_ablation_report.md: PASS
- model_selection_report.md: PASS
- kpi_policy_readout.md: PASS
- release_decision.md: PASS
- data_quality_and_backfill_report.md: PASS
- model_monitoring_baseline_report.md: PASS
- drift_monitoring_report.md: PASS
- explainability_report.md: PASS
- batch_scoring_contract_report.md: PASS

## Performance Evidence Extracts


### baseline_vs_specialty_ablation_report.md

- This report compares vanilla fraud-risk baselines against specialty reliability upgrades.
- | model | pr_auc | roc_auc | precision_at_capacity | recall_at_capacity | fraud_loss_capture_rate | brier | ece | p95_latency_ms_proxy | risk_region_f1_amount |
- | calibrated_operating_champion | 0.3908 | 0.7431 | 0.6709 | 0.3786 | 0.8310 | 0.0700 | 0.0331 | 0.0117 | nan |
- | residual_corrected | 0.4127 | 0.7570 | 0.6709 | 0.3786 | 0.8310 | 0.0701 | 0.0308 | 0.0117 | nan |
- | envelope_pruned | 0.4149 | 0.7613 | 0.6709 | 0.3786 | 0.8310 | 0.0699 | 0.0315 | 0.0117 | 0.7803 |
- The project treats improvements broadly: PR-AUC, Precision@review capacity, fraud-loss capture, calibration, and review-burden tradeoffs are all decision-relevant. The final release decision is made through the KPI simulator and release gates rather than a single AUC metric.

### model_selection_report.md

- "best_pr_auc_model_name": "random_forest",
- "selected_operating_champion": "calibrated_operating_champion"
- - `best_pr_auc_model_name` is the model with the strongest PR-AUC.
- - `policy_model_name` is selected using a fraud-operations utility that balances PR-AUC, Precision@review capacity, fraud-loss capture, and calibration.
- - `selected_operating_champion` is the score source used by downstream residual correction and risk-envelope pruning.

### kpi_policy_readout.md

- Policy scenarios compare fraud capture, review capacity, calibration, and decision score.
- | pr_auc | roc_auc | precision_at_capacity | recall_at_capacity | review_burden | fraud_loss_captured | total_fraud_loss | fraud_loss_capture_rate | false_negative_loss | brier | ece | scenario | decision_score |
- | 0.4127 | 0.7570 | 0.6709 | 0.3786 | 0.0505 | 604325.7400 | 727263.1800 | 0.8310 | 122937.4400 | 0.0701 | 0.0308 | residual_corrected | 0.5702 |
- | 0.4149 | 0.7613 | 0.6709 | 0.3786 | 0.0505 | 604325.7400 | 727263.1800 | 0.8310 | 122937.4400 | 0.0699 | 0.0315 | envelope_pruned | 0.5701 |
- | 0.3908 | 0.7431 | 0.6709 | 0.3786 | 0.0505 | 604325.7400 | 727263.1800 | 0.8310 | 122937.4400 | 0.0700 | 0.0331 | calibrated | 0.5700 |

### release_decision.md

- Decision: **REVIEW**
- "decision": "REVIEW",
- "pr_auc_lift": 0.02411399336541592,
- "precision_at_5pct_lift": 0.0,
- "loss_capture_lift": 0.0,
- "p95_latency_ms": 0.011749289827193393,
- "pr_auc_lift": true,
- "precision_lift": false,
- "loss_capture_lift": false,
- "latency": true,
- This decision is for the local reference framework only. It is not a production approval.

### drift_monitoring_report.md

- Interpretation guide: PSI below 0.10 is usually treated as low shift, 0.10-0.25 as moderate review, and above 0.25 as high shift requiring investigation. These thresholds are heuristic and should be replaced by organization-specific standards in production.

### model_monitoring_baseline_report.md

- "status": "PASS",
- "baseline_type": "local_model_monitor_style_baseline",
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "monitoring_action": "review_if_outside_range_or_missing_rate_exceeds_threshold"
- "claim_boundary": "Local monitoring baseline only. Not an active SageMaker Model Monitor schedule unless deployed on AWS."
- This local artifact mirrors a production monitoring baseline: feature distribution statistics, constraints, and score distribution summaries. It is not an active SageMaker Model Monitor schedule unless deployed on AWS.

### explainability_report.md

- "status": "PASS",
- "method": "permutation_importance_average_precision",
- | feature | importance_mean_pr_auc_drop | importance_std |
- This report provides local permutation-importance diagnostics for the operating champion. It is intended for model-review discussion, not as a substitute for enterprise-approved explainability tooling.

### batch_scoring_contract_report.md

- "status": "PASS",
- "decision_counts": {
- "human_review": 50
- "claim_boundary": "Offline batch scoring sample only. Not a production decision service."
- The generated batch scoring sample documents the score column, decision mapping, decision counts, and human-review routing output. It is an offline contract artifact, not a production decision service.

## Verdict

- Core functional and performance evidence is present.
