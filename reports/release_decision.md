# Release Decision

Decision: **REVIEW**

```json
{
  "decision": "REVIEW",
  "checks": {
    "pr_auc_lift": 0.02411399336541592,
    "precision_at_5pct_lift": 0.0,
    "loss_capture_lift": 0.0,
    "ece": 0.03147920036058359,
    "p95_latency_ms": 0.011749289827193393,
    "utility_lift": 0.0074755228957179565
  },
  "pass_flags": {
    "pr_auc_lift": true,
    "precision_lift": false,
    "loss_capture_lift": false,
    "ece": true,
    "latency": true,
    "utility_lift": true
  }
}
```

This decision is for the local reference framework only. It is not a production approval.
