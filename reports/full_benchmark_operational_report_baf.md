# Full/Large Benchmark Operational Report: baf

## Run Configuration

- dataset: baf
- mode: large_subset
- max_rows: 500000
- loaded_rows: 500000
- runtime_seconds: 9.86
- split: temporal 60/20/20 train/validation/test
- claim boundary: public/proxy benchmark only, not JPMC or proprietary bank data

## Test Metrics

| model | pr_auc | roc_auc | precision_at_5pct | recall_at_5pct | fraud_loss_capture_rate | brier | train_seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| logistic_regression | 0.029151405999857705 | 0.7295246654039914 | 0.0274 | 0.15205327413984462 | 0.26153087326076235 | 0.15618319471408612 | 0.8620970249176025 |
| hist_gradient_boosting | 0.010738843232366294 | 0.49982581124746395 | 0.0122 | 0.06770255271920089 | 0.06847979444591014 | 0.008968039593627518 | 5.4948410987854 |
| mechanism_informed_enhanced | 0.03405912268019525 | 0.7240000047486679 | 0.0466 | 0.2586015538290788 | 0.4507966368047351 | 0.14303242499380597 |  |

## Interpretation

- Baselines show standard fraud-risk model performance under temporal split.
- `mechanism_informed_enhanced` uses validation-selected fusion between the best baseline score and a payment-risk prior.
- This is an operational benchmark extension, not a production deployment or formal model approval.
