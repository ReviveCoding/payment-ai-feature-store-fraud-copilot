# Full/Large Benchmark Operational Report: ieee

## Run Configuration

- dataset: ieee
- mode: large_subset
- max_rows: 300000
- loaded_rows: 300000
- runtime_seconds: 7.46
- split: temporal 60/20/20 train/validation/test
- claim boundary: public/proxy benchmark only, not JPMC or proprietary bank data

## Test Metrics

| model | pr_auc | roc_auc | precision_at_5pct | recall_at_5pct | fraud_loss_capture_rate | brier | train_seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| logistic_regression | 0.08886503007299716 | 0.7145867675415323 | 0.10133333333333333 | 0.13047210300429185 | 0.069939079172568 | 0.31177076118388813 | 0.6496584415435791 |
| hist_gradient_boosting | 0.1320384024418005 | 0.7593004038814894 | 0.17133333333333334 | 0.2206008583690987 | 0.22935070597159019 | 0.03605671612644086 | 3.8326773643493652 |
| mechanism_informed_enhanced | 0.13008643901757538 | 0.7547814224933784 | 0.16933333333333334 | 0.21802575107296138 | 0.2434315979792348 | 0.03602130207324315 |  |

## Interpretation

- Baselines show standard fraud-risk model performance under temporal split.
- `mechanism_informed_enhanced` uses validation-selected fusion between the best baseline score and a payment-risk prior.
- This is an operational benchmark extension, not a production deployment or formal model approval.
