# Data Quality and Backfill Idempotence Report

## Data quality baseline

```json
{
  "status": "PASS",
  "rows": {
    "events": 6250,
    "features": 6250
  },
  "null_rates": {
    "events": {
      "event_id": 0.0,
      "event_time": 0.0,
      "account_id_hash": 0.0,
      "amount": 0.0,
      "risk_label": 0.0,
      "dataset_source": 0.0
    },
    "features": {
      "event_id": 0.0,
      "event_time": 0.0,
      "account_id_hash": 0.0,
      "amount": 0.0,
      "rule_risk_prior": 0.0,
      "txn_count_prior": 0.0,
      "failed_txn_rate_prior": 0.0,
      "amount_zscore_account": 0.0
    }
  },
  "duplicate_rates": {
    "events": 0.0,
    "features": 0.0
  },
  "amount_stats": {
    "min": 1.896,
    "p50": 424.935,
    "p95": 140185.8599999985,
    "max": 3776389.09,
    "non_positive_rate": 0.0
  },
  "source_counts": {
    "events": {
      "paysim_style_sample": 1378,
      "ieee_cis_public": 1250,
      "baf_public": 1250,
      "paysim_public": 1250,
      "baf_style_sample": 1122
    },
    "features": {
      "paysim_style_sample": 1378,
      "ieee_cis_public": 1250,
      "baf_public": 1250,
      "paysim_public": 1250,
      "baf_style_sample": 1122
    }
  },
  "deterministic_feature_hash": "0b1153b89a525c95f91f9eb08c2845662ad503e6393eb0cc99ddd8f21f2e6118",
  "checks": {
    "required_event_columns_present": true,
    "required_feature_columns_present": true,
    "event_duplicate_rate_ok": true,
    "feature_duplicate_rate_ok": true,
    "event_null_rate_ok": true,
    "feature_null_rate_ok": true,
    "amount_values_positive": true,
    "dataset_sources_present": true,
    "feature_sources_present": true
  }
}
```

## Backfill idempotence

```json
{
  "status": "PASS",
  "first_rows": 6250,
  "second_rows": 6250,
  "first_hash": "c66bb4b99109f7a07962854b7bc1f6de0c4e3f2e5fe73575b012a6af61f42e72",
  "second_hash": "c66bb4b99109f7a07962854b7bc1f6de0c4e3f2e5fe73575b012a6af61f42e72",
  "rule": "A deterministic rerun over the same inputs should produce identical feature hashes and row counts."
}
```

## Interpretation

This report hardens the feature pipeline beyond simple row-count checks. It verifies required columns, null rates, duplicate event IDs, amount sanity, source coverage, and deterministic feature hashes for repeatable batch backfills.
