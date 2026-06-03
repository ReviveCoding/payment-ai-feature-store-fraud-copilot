# Full Benchmark Operational Summary

This report aggregates PaySim full and BAF/IEEE large-subset operational benchmark results.

| dataset | model | rows | positive_rate | pr_auc | roc_auc | precision_at_5pct | recall_at_5pct | fraud_loss_capture_rate | brier | train_seconds | selected_alpha | base_model |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| paysim | logistic_regression | 1272524 | 0.003343 | 0.116104 | 0.916668 | 0.031528 | 0.471556 | 0.889707 | 0.076157 | 16.248426 |  |  |
| paysim | hist_gradient_boosting | 1272524 | 0.003343 | 0.056619 | 0.683528 | 0.035033 | 0.523977 | 0.162470 | 0.004855 | 10.501544 |  |  |
| paysim | mechanism_informed_enhanced | 1272524 | 0.003343 | 0.085493 | 0.854412 | 0.041210 | 0.616361 | 0.667706 | 0.005033 |  | 0.050000 | hist_gradient_boosting |
| baf | logistic_regression | 100000 | 0.009010 | 0.029151 | 0.729525 | 0.027400 | 0.152053 | 0.261531 | 0.156183 | 0.862097 |  |  |
| baf | hist_gradient_boosting | 100000 | 0.009010 | 0.010739 | 0.499826 | 0.012200 | 0.067703 | 0.068480 | 0.008968 | 5.494841 |  |  |
| baf | mechanism_informed_enhanced | 100000 | 0.009010 | 0.034059 | 0.724000 | 0.046600 | 0.258602 | 0.450797 | 0.143032 |  | 0.500000 | logistic_regression |
| ieee | logistic_regression | 60000 | 0.038833 | 0.088865 | 0.714587 | 0.101333 | 0.130472 | 0.069939 | 0.311771 | 0.649658 |  |  |
| ieee | hist_gradient_boosting | 60000 | 0.038833 | 0.132038 | 0.759300 | 0.171333 | 0.220601 | 0.229351 | 0.036057 | 3.832677 |  |  |
| ieee | mechanism_informed_enhanced | 60000 | 0.038833 | 0.130086 | 0.754781 | 0.169333 | 0.218026 | 0.243432 | 0.036021 |  | 0.050000 | hist_gradient_boosting |

## Interpretation

- Do not claim the enhanced method wins every metric.
- Use metric-specific claims: review-capacity recall/precision, PR-AUC, fraud-loss capture, and calibration can have different winners.
- This is public/proxy benchmark evidence, not JPMC or proprietary bank production evidence.

## paysim metric winners

- Best pr_auc: `logistic_regression` = 0.116104
- Best roc_auc: `logistic_regression` = 0.916668
- Best precision_at_5pct: `mechanism_informed_enhanced` = 0.041210
- Best recall_at_5pct: `mechanism_informed_enhanced` = 0.616361
- Best fraud_loss_capture_rate: `logistic_regression` = 0.889707
- Best brier: `hist_gradient_boosting` = 0.004855

## baf metric winners

- Best pr_auc: `mechanism_informed_enhanced` = 0.034059
- Best roc_auc: `logistic_regression` = 0.729525
- Best precision_at_5pct: `mechanism_informed_enhanced` = 0.046600
- Best recall_at_5pct: `mechanism_informed_enhanced` = 0.258602
- Best fraud_loss_capture_rate: `mechanism_informed_enhanced` = 0.450797
- Best brier: `hist_gradient_boosting` = 0.008968

## ieee metric winners

- Best pr_auc: `hist_gradient_boosting` = 0.132038
- Best roc_auc: `hist_gradient_boosting` = 0.759300
- Best precision_at_5pct: `hist_gradient_boosting` = 0.171333
- Best recall_at_5pct: `hist_gradient_boosting` = 0.220601
- Best fraud_loss_capture_rate: `mechanism_informed_enhanced` = 0.243432
- Best brier: `mechanism_informed_enhanced` = 0.036021
