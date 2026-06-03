# Baseline vs Specialty Ablation Report

This report compares vanilla fraud-risk baselines against specialty reliability upgrades.

| model | pr_auc | roc_auc | precision_at_capacity | recall_at_capacity | fraud_loss_capture_rate | brier | ece | p95_latency_ms_proxy | risk_region_f1_amount |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| logistic_regression | 0.1589 | 0.6446 | 0.1772 | 0.1000 | 0.1518 | 0.4026 | 0.5514 | 0.0008 | nan |
| random_forest | 0.3808 | 0.7330 | 0.6582 | 0.3714 | 0.7985 | 0.0696 | 0.0375 | 0.0098 | nan |
| gradient_boosting | 0.3752 | 0.7382 | 0.5949 | 0.3357 | 0.7781 | 0.0722 | 0.0504 | 0.0016 | nan |
| calibrated_operating_champion | 0.3908 | 0.7431 | 0.6709 | 0.3786 | 0.8310 | 0.0700 | 0.0331 | 0.0117 | nan |
| selected_operating_champion | 0.3908 | 0.7431 | 0.6709 | 0.3786 | 0.8310 | 0.0700 | 0.0331 | 0.0117 | nan |
| residual_corrected | 0.4127 | 0.7570 | 0.6709 | 0.3786 | 0.8310 | 0.0701 | 0.0308 | 0.0117 | nan |
| envelope_pruned | 0.4149 | 0.7613 | 0.6709 | 0.3786 | 0.8310 | 0.0699 | 0.0315 | 0.0117 | 0.7803 |
| final_operating_policy | 0.4149 | 0.7613 | 0.6709 | 0.3786 | 0.8310 | 0.0699 | 0.0315 | 0.0117 | nan |

## Interpretation

The project treats improvements broadly: PR-AUC, Precision@review capacity, fraud-loss capture, calibration, and review-burden tradeoffs are all decision-relevant. The final release decision is made through the KPI simulator and release gates rather than a single AUC metric.
