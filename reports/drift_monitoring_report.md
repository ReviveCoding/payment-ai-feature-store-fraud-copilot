# Drift Monitoring Report

Population Stability Index (PSI) is calculated on the temporal train/test split for core feature-store columns.

```json
{
  "amount": 2.709243172613695,
  "amount_log": 2.709243172613695,
  "cross_border_flag": 0.0,
  "rule_risk_prior": 2.474241772034097,
  "txn_count_prior": 10.099949005734837,
  "amount_sum_prior": 7.532884503494819,
  "failed_txn_rate_prior": 0.0,
  "amount_zscore_account": 2.7071547169146606
}
```

Interpretation guide: PSI below 0.10 is usually treated as low shift, 0.10-0.25 as moderate review, and above 0.25 as high shift requiring investigation. These thresholds are heuristic and should be replaced by organization-specific standards in production.
