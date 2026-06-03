# Capacity Sweep Operational Report: paysim

## Run Configuration

- dataset: paysim
- mode: full
- max_rows: full
- loaded_rows: 6362620
- test_rows: 1272524
- runtime_seconds: 88.68
- split: temporal 60/20/20 train/validation/test
- best_base_model_by_validation_pr_auc: hist_gradient_boosting
- selected_alpha_from_validation: 0.05
- claim boundary: public/proxy benchmark only, not JPMC or proprietary bank data

## Global Ranking / Calibration Metrics

| dataset | model | rows | positive_rate | pr_auc | roc_auc | brier | train_seconds | selected_alpha | base_model |
|---|---|---|---|---|---|---|---|---|---|
| paysim | logistic_regression | 1272524 | 0.003343 | 0.116104 | 0.916668 | 0.076157 | 12.904672 |  |  |
| paysim | hist_gradient_boosting | 1272524 | 0.003343 | 0.056619 | 0.683528 | 0.004855 | 10.415334 |  |  |
| paysim | mechanism_informed_enhanced | 1272524 | 0.003343 | 0.085493 | 0.854412 | 0.005033 |  | 0.050000 | hist_gradient_boosting |

## Capacity Sweep Metrics

| dataset | model | capacity_pct | top_k | precision_at_capacity | recall_at_capacity | fraud_loss_capture_rate | false_negative_loss | reviewed_fraud_count | true_fraud_count |
|---|---|---|---|---|---|---|---|---|---|
| paysim | logistic_regression | 1 | 12725 | 0.114263 | 0.341796 | 0.840845 | 1063906423.370000 | 1454 | 4254 |
| paysim | logistic_regression | 2 | 25450 | 0.065658 | 0.392807 | 0.867829 | 883529190.159999 | 1671 | 4254 |
| paysim | logistic_regression | 5 | 63626 | 0.031528 | 0.471556 | 0.889707 | 737278533.640000 | 2006 | 4254 |
| paysim | logistic_regression | 10 | 127252 | 0.026577 | 0.795016 | 0.971099 | 193195463.989999 | 3382 | 4254 |
| paysim | hist_gradient_boosting | 1 | 12725 | 0.122043 | 0.365068 | 0.109373 | 5953602293.670000 | 1553 | 4254 |
| paysim | hist_gradient_boosting | 2 | 25450 | 0.079764 | 0.477198 | 0.154393 | 5652655276.270000 | 2030 | 4254 |
| paysim | hist_gradient_boosting | 5 | 63626 | 0.035033 | 0.523977 | 0.162470 | 5598663303.330000 | 2229 | 4254 |
| paysim | hist_gradient_boosting | 10 | 127252 | 0.018695 | 0.559238 | 0.165845 | 5576102232.209999 | 2379 | 4254 |
| paysim | mechanism_informed_enhanced | 1 | 12725 | 0.126523 | 0.378467 | 0.637139 | 2425631912.740000 | 1610 | 4254 |
| paysim | mechanism_informed_enhanced | 2 | 25450 | 0.103026 | 0.616361 | 0.667706 | 2221296192.170000 | 2622 | 4254 |
| paysim | mechanism_informed_enhanced | 5 | 63626 | 0.041210 | 0.616361 | 0.667706 | 2221296192.170000 | 2622 | 4254 |
| paysim | mechanism_informed_enhanced | 10 | 127252 | 0.026239 | 0.784908 | 0.976522 | 156942752.650000 | 3339 | 4254 |

## Capacity-specific Winners


### Top 1% review capacity

- Best precision_at_capacity: `mechanism_informed_enhanced` = 0.126523
- Best recall_at_capacity: `mechanism_informed_enhanced` = 0.378467
- Best fraud_loss_capture_rate: `logistic_regression` = 0.840845

### Top 2% review capacity

- Best precision_at_capacity: `mechanism_informed_enhanced` = 0.103026
- Best recall_at_capacity: `mechanism_informed_enhanced` = 0.616361
- Best fraud_loss_capture_rate: `logistic_regression` = 0.867829

### Top 5% review capacity

- Best precision_at_capacity: `mechanism_informed_enhanced` = 0.041210
- Best recall_at_capacity: `mechanism_informed_enhanced` = 0.616361
- Best fraud_loss_capture_rate: `logistic_regression` = 0.889707

### Top 10% review capacity

- Best precision_at_capacity: `logistic_regression` = 0.026577
- Best recall_at_capacity: `logistic_regression` = 0.795016
- Best fraud_loss_capture_rate: `mechanism_informed_enhanced` = 0.976522

## Interpretation

- This report evaluates operational behavior under limited analyst-review capacity.
- Precision@capacity asks how accurate the review queue is.
- Recall@capacity asks how many fraud events are captured within the review queue.
- Fraud-loss capture asks how much fraud amount is captured within the review queue.
- Do not claim one model is globally best unless it wins the relevant operating metric and capacity range.
- This is not production approval or real bank deployment evidence.
