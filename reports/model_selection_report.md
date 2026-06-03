# Model Selection Report

This project separates statistical ranking performance from operating-policy usefulness.

```json
{
  "best_pr_auc_model_name": "random_forest",
  "policy_model_name": "random_forest",
  "selected_operating_champion": "calibrated_operating_champion"
}
```

- `best_pr_auc_model_name` is the model with the strongest PR-AUC.
- `policy_model_name` is selected using a fraud-operations utility that balances PR-AUC, Precision@review capacity, fraud-loss capture, and calibration.
- `selected_operating_champion` is the score source used by downstream residual correction and risk-envelope pruning.
