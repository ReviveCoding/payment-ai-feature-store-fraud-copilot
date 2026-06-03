# Spark/PySpark Execution Artifact

This artifact documents a local Spark/PySpark batch scoring benchmark for the payment fraud-risk framework.

## What was executed

- Spark DataFrame ingestion from PaySim public/proxy fraud data
- Spark SQL feature engineering
- Temporal train/validation/test split
- Spark ML Logistic Regression training
- Batch scoring on the test split
- Parquet feature-store-style output
- Parquet scored-batch output
- Spark ML pipeline model artifact
- Model-registry-style JSON metadata with metric and claim-boundary fields

## Claim boundary

This is a local Spark/PySpark benchmark artifact. It is not AWS EMR, not SageMaker training, not JPMC data, not proprietary bank data, and not a production deployment.

## Main report

See `reports/spark_pyspark_batch_scoring_report.md`.

## Run ID

`paysim_spark_lr_500k_20260603T230150Z`
