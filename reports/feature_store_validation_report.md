# Feature Store Validation Report

## Schema validation

```json
{
  "rows": 6250,
  "missing_required_columns": [],
  "required_null_rates": {
    "dataset_source": 0.0,
    "event_id": 0.0,
    "event_time": 0.0,
    "account_id_hash": 0.0,
    "counterparty_id_hash": 0.02752,
    "amount": 0.0,
    "currency": 0.0,
    "channel": 0.0,
    "payment_type": 0.0,
    "payment_status": 0.0,
    "risk_label": 0.0
  },
  "valid": true
}
```

## Spark-SQL-style feature validation

```json
{
  "row_count": 6250,
  "label_rate": 0.04352,
  "feature_null_rate_max": 0.0,
  "event_time_min": "1970-01-01 00:00:00.000086400",
  "event_time_max": "2025-03-01 23:10:00",
  "partition_columns": [
    "dataset_source",
    "event_date"
  ]
}
```

## Point-in-time validation

```json
{
  "point_in_time_valid": true,
  "checked_rows": 6250,
  "rule": "txn_count_prior equals number of prior events within account"
}
```

## Offline/online parity

```json
{
  "matched_accounts": 1899,
  "event_match_rate": 1.0,
  "max_rule_prior_diff": 0.0,
  "parity_pass": true
}
```

## Offline store manifest

- Format: `csv_fallback_parquet_recommended`
- Rows: `6250`
- Partitions: `123`

Note: the demo writes Parquet when a Parquet engine is installed; otherwise it writes a CSV fallback while preserving partitioning and manifest metadata.
