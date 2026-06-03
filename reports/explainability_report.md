# Explainability Report

## Summary

```json
{
  "status": "PASS",
  "method": "permutation_importance_average_precision",
  "rows_evaluated": 600,
  "artifact": "C:\\Users\\bjw-0\\Downloads\\payment-ai-feature-store-fraud-copilot\\outputs\\feature_importance.csv",
  "claim_boundary": "Local explainability diagnostic only; not a formal SHAP/enterprise model-risk explanation package."
}
```

## Top local feature attribution diagnostics

| feature | importance_mean_pr_auc_drop | importance_std |
| --- | --- | --- |
| amount_log | 0.0347 | 0.0246 |
| amount | 0.0235 | 0.0265 |
| rule_risk_prior | 0.0088 | 0.0173 |
| amount_sum_prior | 0.0058 | 0.0044 |
| failed_txn_rate_prior | 0.0038 | 0.0058 |
| cross_border_flag | 0.0007 | 0.0246 |
| rejected_flag | 0.0002 | 0.0003 |
| high_risk_corridor_flag | -0.0044 | 0.0019 |

This report provides local permutation-importance diagnostics for the operating champion. It is intended for model-review discussion, not as a substitute for enterprise-approved explainability tooling.
