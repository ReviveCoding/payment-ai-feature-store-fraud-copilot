# Capacity Sweep Operational Report: ieee

## Run Configuration

- dataset: ieee
- mode: large_subset
- max_rows: 300000
- loaded_rows: 300000
- test_rows: 60000
- runtime_seconds: 7.48
- split: temporal 60/20/20 train/validation/test
- best_base_model_by_validation_pr_auc: hist_gradient_boosting
- selected_alpha_from_validation: 0.05
- claim boundary: public/proxy benchmark only, not JPMC or proprietary bank data

## Global Ranking / Calibration Metrics

| dataset | model | rows | positive_rate | pr_auc | roc_auc | brier | train_seconds | selected_alpha | base_model |
|---|---|---|---|---|---|---|---|---|---|
| ieee | logistic_regression | 60000 | 0.038833 | 0.088865 | 0.714587 | 0.311771 | 0.400797 |  |  |
| ieee | hist_gradient_boosting | 60000 | 0.038833 | 0.132038 | 0.759300 | 0.036057 | 4.173465 |  |  |
| ieee | mechanism_informed_enhanced | 60000 | 0.038833 | 0.130086 | 0.754781 | 0.036021 |  | 0.050000 | hist_gradient_boosting |

## Capacity Sweep Metrics

| dataset | model | capacity_pct | top_k | precision_at_capacity | recall_at_capacity | fraud_loss_capture_rate | false_negative_loss | reviewed_fraud_count | true_fraud_count |
|---|---|---|---|---|---|---|---|---|---|
| ieee | logistic_regression | 1 | 600 | 0.120000 | 0.030901 | 0.029337 | 304574.312000 | 72 | 2330 |
| ieee | logistic_regression | 2 | 1200 | 0.090833 | 0.046781 | 0.037615 | 301976.730000 | 109 | 2330 |
| ieee | logistic_regression | 5 | 3000 | 0.101333 | 0.130472 | 0.069939 | 291834.100000 | 304 | 2330 |
| ieee | logistic_regression | 10 | 6000 | 0.118667 | 0.305579 | 0.127535 | 273761.792000 | 712 | 2330 |
| ieee | hist_gradient_boosting | 1 | 600 | 0.253333 | 0.065236 | 0.118128 | 276713.553000 | 152 | 2330 |
| ieee | hist_gradient_boosting | 2 | 1200 | 0.204167 | 0.105150 | 0.166785 | 261445.949000 | 245 | 2330 |
| ieee | hist_gradient_boosting | 5 | 3000 | 0.171333 | 0.220601 | 0.229351 | 241813.991000 | 514 | 2330 |
| ieee | hist_gradient_boosting | 10 | 6000 | 0.138833 | 0.357511 | 0.349823 | 204012.205000 | 833 | 2330 |
| ieee | mechanism_informed_enhanced | 1 | 600 | 0.248333 | 0.063948 | 0.116693 | 277163.553000 | 149 | 2330 |
| ieee | mechanism_informed_enhanced | 2 | 1200 | 0.204167 | 0.105150 | 0.167939 | 261083.854000 | 245 | 2330 |
| ieee | mechanism_informed_enhanced | 5 | 3000 | 0.169333 | 0.218026 | 0.243432 | 237395.695000 | 508 | 2330 |
| ieee | mechanism_informed_enhanced | 10 | 6000 | 0.136333 | 0.351073 | 0.363769 | 199636.384000 | 818 | 2330 |

## Capacity-specific Winners


### Top 1% review capacity

- Best precision_at_capacity: `hist_gradient_boosting` = 0.253333
- Best recall_at_capacity: `hist_gradient_boosting` = 0.065236
- Best fraud_loss_capture_rate: `hist_gradient_boosting` = 0.118128

### Top 2% review capacity

- Best precision_at_capacity: `hist_gradient_boosting` = 0.204167
- Best recall_at_capacity: `hist_gradient_boosting` = 0.105150
- Best fraud_loss_capture_rate: `mechanism_informed_enhanced` = 0.167939

### Top 5% review capacity

- Best precision_at_capacity: `hist_gradient_boosting` = 0.171333
- Best recall_at_capacity: `hist_gradient_boosting` = 0.220601
- Best fraud_loss_capture_rate: `mechanism_informed_enhanced` = 0.243432

### Top 10% review capacity

- Best precision_at_capacity: `hist_gradient_boosting` = 0.138833
- Best recall_at_capacity: `hist_gradient_boosting` = 0.357511
- Best fraud_loss_capture_rate: `mechanism_informed_enhanced` = 0.363769

## Interpretation

- This report evaluates operational behavior under limited analyst-review capacity.
- Precision@capacity asks how accurate the review queue is.
- Recall@capacity asks how many fraud events are captured within the review queue.
- Fraud-loss capture asks how much fraud amount is captured within the review queue.
- Do not claim one model is globally best unless it wins the relevant operating metric and capacity range.
- This is not production approval or real bank deployment evidence.
