# Spark/PySpark Batch Scoring Benchmark Report

## Run Configuration

- run_id: paysim_spark_lr_500k_20260603T230150Z
- source_csv: C:\Users\bjw-0\Downloads\payment-ai-feature-store-fraud-copilot\data\raw\paysim\PS_20174392719_1491204439457_log.csv
- max_rows: 500000
- Spark master: local[*]
- Python: 3.11.9
- claim boundary: public/proxy benchmark only; not JPMC data, proprietary bank data, or production deployment

## Dataset and Split

| split | rows |
|---|---|
| raw_loaded | 500000 |
| features | 500000 |
| fraud_rows | 233 |
| train | 300000 |
| validation | 100000 |
| test | 100000 |

## Global Test Metrics

| pr_auc | roc_auc | brier | train_seconds | score_seconds | runtime_seconds |
|---|---|---|---|---|---|
| 0.071944 | 0.933096 | 0.022810 | 5.938474 | 0.980414 | 34.669411 |

## Capacity Sweep Metrics

| capacity_pct | top_k | precision_at_capacity | recall_at_capacity | fraud_loss_capture_rate | false_negative_loss | reviewed_fraud_count | true_fraud_count |
|---|---|---|---|---|---|---|---|
| 1 | 1000 | 0.017000 | 0.586207 | 0.901382 | 4137588.270000 | 17 | 29 |
| 2 | 2000 | 0.008500 | 0.586207 | 0.901382 | 4137588.270000 | 17 | 29 |
| 5 | 5000 | 0.004400 | 0.758621 | 0.958835 | 1727092.890000 | 22 | 29 |
| 10 | 10000 | 0.002200 | 0.758621 | 0.958835 | 1727092.890000 | 22 | 29 |

## Artifacts

- feature_store_parquet: `data\feature_store_spark\paysim_spark_lr_500k_20260603T230150Z`
- scored_batch_parquet: `outputs\spark_batch_benchmark\paysim_spark_lr_500k_20260603T230150Z\scored_test_parquet`
- spark_model_path: `models\paysim_spark_lr_500k_20260603T230150Z_spark_pipeline_model`
- model_registry_json: `data\model_registry\paysim_spark_lr_500k_20260603T230150Z_model_registry.json`
- metrics_json: `outputs\spark_batch_benchmark\paysim_spark_lr_500k_20260603T230150Z\spark_batch_scoring_metrics.json`

## Resume-Safe Interpretation

- This run provides a real local Spark/PySpark execution artifact for batch feature engineering, model training, scoring, Parquet output, and registry-style metadata.
- It does not claim AWS EMR execution, SageMaker training execution, real bank data, JPMC data, or production deployment.
- Use this as supporting evidence for PySpark-compatible distributed processing and feature-store-style batch scoring.

