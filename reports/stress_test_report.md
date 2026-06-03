# Small-Data Stress Test Report

These checks validate score behavior on local/synthetic data before any full public benchmark or cloud run.

```json
{
  "base": {
    "pr_auc": 0.41487611128557,
    "roc_auc": 0.7613166348760165,
    "precision_at_capacity": 0.6708860759493671,
    "recall_at_capacity": 0.37857142857142856,
    "review_burden": 0.05054382597568778,
    "fraud_loss_captured": 604325.74,
    "total_fraud_loss": 727263.18,
    "fraud_loss_capture_rate": 0.8309588009116589,
    "false_negative_loss": 122937.44000000006,
    "brier": 0.06987891872043339,
    "ece": 0.03147920036058359
  },
  "amount_shock": {
    "pr_auc": 0.41487611128557,
    "roc_auc": 0.7613166348760165,
    "precision_at_capacity": 0.6708860759493671,
    "recall_at_capacity": 0.37857142857142856,
    "review_burden": 0.05054382597568778,
    "fraud_loss_captured": 901259.5950000001,
    "total_fraud_loss": 1024197.035,
    "fraud_loss_capture_rate": 0.8799670026383156,
    "false_negative_loss": 122937.43999999994,
    "brier": 0.06987891872043339,
    "ece": 0.03147920036058359
  },
  "score_compression_drift": {
    "pr_auc": 0.41487611128557,
    "roc_auc": 0.7613166348760165,
    "precision_at_capacity": 0.6708860759493671,
    "recall_at_capacity": 0.37857142857142856,
    "review_burden": 0.05054382597568778,
    "fraud_loss_captured": 604325.74,
    "total_fraud_loss": 727263.18,
    "fraud_loss_capture_rate": 0.8309588009116589,
    "false_negative_loss": 122937.44000000006,
    "brier": 0.07617025405215148,
    "ece": 0.08937728191878011
  },
  "without_envelope_pruning": {
    "pr_auc": 0.4127481958914157,
    "roc_auc": 0.7569797209115551,
    "precision_at_capacity": 0.6708860759493671,
    "recall_at_capacity": 0.37857142857142856,
    "review_burden": 0.05054382597568778,
    "fraud_loss_captured": 604325.74,
    "total_fraud_loss": 727263.18,
    "fraud_loss_capture_rate": 0.8309588009116589,
    "false_negative_loss": 122937.44000000006,
    "brier": 0.07014822898006368,
    "ece": 0.030770496536584903
  },
  "notes": [
    "Small-data stress tests are sanity checks, not production validation.",
    "Amount-shock evaluates sensitivity of fraud-loss capture.",
    "Score-compression drift evaluates whether ranking metrics are stable under mild calibration drift."
  ]
}
```

The stress tests are not production validation. They are intended to show that the framework includes robustness checks for payment amount shocks, score compression drift, and envelope-pruning contribution.
