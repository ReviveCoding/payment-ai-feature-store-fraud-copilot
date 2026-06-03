# Model Card: Payment Fraud-Risk Classifier

## Intended use

Offline evaluation of fraud-risk ranking and review-routing policies on public-style/synthetic payment data.

## Not intended for

Production fraud decisions, real customer decisions, or regulatory approval.

## Data

Generated public-style fraud data and synthetic ISO 20022 payment events when available locally.

## Metrics

See `baseline_vs_specialty_ablation_report.md` and `kpi_policy_readout.md`.

## Limitations

Public/proxy/synthetic data cannot fully represent proprietary payment networks, customer behavior, fraud operations, or production model risk constraints.
