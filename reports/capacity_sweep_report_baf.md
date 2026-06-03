# Capacity Sweep Operational Report: baf

## Run Configuration

- dataset: baf
- mode: large_subset
- max_rows: 500000
- loaded_rows: 500000
- test_rows: 100000
- runtime_seconds: 6.92
- split: temporal 60/20/20 train/validation/test
- best_base_model_by_validation_pr_auc: logistic_regression
- selected_alpha_from_validation: 0.9
- claim boundary: public/proxy benchmark only, not JPMC or proprietary bank data

## Global Ranking / Calibration Metrics

| dataset | model | rows | positive_rate | pr_auc | roc_auc | brier | train_seconds | selected_alpha | base_model |
|---|---|---|---|---|---|---|---|---|---|
| baf | logistic_regression | 100000 | 0.009010 | 0.029151 | 0.729525 | 0.156183 | 0.785431 |  |  |
| baf | hist_gradient_boosting | 100000 | 0.009010 | 0.010739 | 0.499826 | 0.008968 | 3.225061 |  |  |
| baf | mechanism_informed_enhanced | 100000 | 0.009010 | 0.034132 | 0.723784 | 0.146947 |  | 0.900000 | logistic_regression |

## Capacity Sweep Metrics

| dataset | model | capacity_pct | top_k | precision_at_capacity | recall_at_capacity | fraud_loss_capture_rate | false_negative_loss | reviewed_fraud_count | true_fraud_count |
|---|---|---|---|---|---|---|---|---|---|
| baf | logistic_regression | 1 | 1000 | 0.079000 | 0.087680 | 0.174354 | 719790.000000 | 79 | 901 |
| baf | logistic_regression | 2 | 2000 | 0.054000 | 0.119867 | 0.227692 | 673290.000000 | 108 | 901 |
| baf | logistic_regression | 5 | 5000 | 0.027400 | 0.152053 | 0.261531 | 643790.000000 | 137 | 901 |
| baf | logistic_regression | 10 | 10000 | 0.025400 | 0.281909 | 0.433361 | 493990.000000 | 254 | 901 |
| baf | hist_gradient_boosting | 1 | 1000 | 0.026000 | 0.028857 | 0.047030 | 830790.000000 | 26 | 901 |
| baf | hist_gradient_boosting | 2 | 2000 | 0.018500 | 0.041065 | 0.060565 | 818990.000000 | 37 | 901 |
| baf | hist_gradient_boosting | 5 | 5000 | 0.012200 | 0.067703 | 0.068480 | 812090.000000 | 61 | 901 |
| baf | hist_gradient_boosting | 10 | 10000 | 0.016600 | 0.184240 | 0.277131 | 630190.000000 | 166 | 901 |
| baf | mechanism_informed_enhanced | 1 | 1000 | 0.079000 | 0.087680 | 0.174354 | 719790.000000 | 79 | 901 |
| baf | mechanism_informed_enhanced | 2 | 2000 | 0.054500 | 0.120977 | 0.233542 | 668190.000000 | 109 | 901 |
| baf | mechanism_informed_enhanced | 5 | 5000 | 0.046600 | 0.258602 | 0.450797 | 478790.000000 | 233 | 901 |
| baf | mechanism_informed_enhanced | 10 | 10000 | 0.035600 | 0.395117 | 0.662430 | 294290.000000 | 356 | 901 |

## Capacity-specific Winners


### Top 1% review capacity

- Best precision_at_capacity: `logistic_regression` = 0.079000
- Best recall_at_capacity: `logistic_regression` = 0.087680
- Best fraud_loss_capture_rate: `logistic_regression` = 0.174354

### Top 2% review capacity

- Best precision_at_capacity: `mechanism_informed_enhanced` = 0.054500
- Best recall_at_capacity: `mechanism_informed_enhanced` = 0.120977
- Best fraud_loss_capture_rate: `mechanism_informed_enhanced` = 0.233542

### Top 5% review capacity

- Best precision_at_capacity: `mechanism_informed_enhanced` = 0.046600
- Best recall_at_capacity: `mechanism_informed_enhanced` = 0.258602
- Best fraud_loss_capture_rate: `mechanism_informed_enhanced` = 0.450797

### Top 10% review capacity

- Best precision_at_capacity: `mechanism_informed_enhanced` = 0.035600
- Best recall_at_capacity: `mechanism_informed_enhanced` = 0.395117
- Best fraud_loss_capture_rate: `mechanism_informed_enhanced` = 0.662430

## Interpretation

- This report evaluates operational behavior under limited analyst-review capacity.
- Precision@capacity asks how accurate the review queue is.
- Recall@capacity asks how many fraud events are captured within the review queue.
- Fraud-loss capture asks how much fraud amount is captured within the review queue.
- Do not claim one model is globally best unless it wins the relevant operating metric and capacity range.
- This is not production approval or real bank deployment evidence.
