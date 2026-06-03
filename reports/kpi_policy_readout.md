# KPI Policy Readout

Policy scenarios compare fraud capture, review capacity, calibration, and decision score.

| pr_auc | roc_auc | precision_at_capacity | recall_at_capacity | review_burden | fraud_loss_captured | total_fraud_loss | fraud_loss_capture_rate | false_negative_loss | brier | ece | scenario | decision_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.4127 | 0.7570 | 0.6709 | 0.3786 | 0.0505 | 604325.7400 | 727263.1800 | 0.8310 | 122937.4400 | 0.0701 | 0.0308 | residual_corrected | 0.5702 |
| 0.4149 | 0.7613 | 0.6709 | 0.3786 | 0.0505 | 604325.7400 | 727263.1800 | 0.8310 | 122937.4400 | 0.0699 | 0.0315 | envelope_pruned | 0.5701 |
| 0.3908 | 0.7431 | 0.6709 | 0.3786 | 0.0505 | 604325.7400 | 727263.1800 | 0.8310 | 122937.4400 | 0.0700 | 0.0331 | calibrated | 0.5700 |
