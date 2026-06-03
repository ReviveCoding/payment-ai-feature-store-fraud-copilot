# Public Dataset Extension Report

This project is runnable without external downloads, but it includes dataset-specific adapters for user-supplied public fraud benchmarks.

```json
{
  "loaded_sources": [
    {
      "source": "paysim_public",
      "path": "C:/Users/bjw-0/Downloads/payment-ai-feature-store-fraud-copilot/data/raw/paysim/PS_20174392719_1491204439457_log.csv",
      "rows": 1250
    },
    {
      "source": "baf_public",
      "path": "C:/Users/bjw-0/Downloads/payment-ai-feature-store-fraud-copilot/data/raw/baf/Base.csv",
      "rows": 1250
    },
    {
      "source": "ieee_cis_public",
      "path": "C:/Users/bjw-0/Downloads/payment-ai-feature-store-fraud-copilot/data/raw/ieee_cis/train_transaction.csv",
      "rows": 1250
    }
  ],
  "skipped_sources": [],
  "max_rows_per_source": 1250
}
```

## Supported adapter paths

- PaySim-style CSV: `configs/dataset_sources.yaml -> local_optional_paths.paysim_csv`
- Bank Account Fraud Dataset Suite CSV: `configs/dataset_sources.yaml -> local_optional_paths.baf_csv`
- IEEE-CIS transaction CSV: `configs/dataset_sources.yaml -> local_optional_paths.ieee_cis_transaction_csv`
- IEEE-CIS identity CSV: `configs/dataset_sources.yaml -> local_optional_paths.ieee_cis_identity_csv`

If these files are not present, `make run-demo` uses generated public-style payment-fraud samples so that the engineering, feature-store, and validation pipeline remains reproducible.
