# Full/Large Benchmark Operational Report: paysim

## Run Configuration

- dataset: paysim
- mode: full
- max_rows: full
- loaded_rows: 6362620
- runtime_seconds: 76.44
- split: temporal 60/20/20 train/validation/test
- claim boundary: public/proxy benchmark only, not JPMC or proprietary bank data

## Test Metrics

| model | pr_auc | roc_auc | precision_at_5pct | recall_at_5pct | fraud_loss_capture_rate | brier | train_seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| logistic_regression | 0.11610422852799371 | 0.9166678464145391 | 0.03152799170150567 | 0.4715561824165491 | 0.8897071122320364 | 0.07615669586731945 | 16.24842596054077 |
| hist_gradient_boosting | 0.05661910201486419 | 0.6835277087039879 | 0.03503284820670795 | 0.5239774330042313 | 0.16247019926623482 | 0.00485500307460129 | 10.501543998718262 |
| mechanism_informed_enhanced | 0.08549262725351799 | 0.854412216636377 | 0.04120956841542765 | 0.616361071932299 | 0.6677060833266625 | 0.0050331840899227685 |  |

## Interpretation

- Baselines show standard fraud-risk model performance under temporal split.
- `mechanism_informed_enhanced` uses validation-selected fusion between the best baseline score and a payment-risk prior.
- This is an operational benchmark extension, not a production deployment or formal model approval.
