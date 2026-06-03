# Optional EMR / SageMaker Runbook

This project does not require AWS credentials for the default demo. The steps below are a compatibility guide only.

## Optional EMR-compatible path

1. Upload sample canonical events to S3.
2. Package `src/spark_jobs/build_payment_features.py` as the feature processing entry point.
3. Run an EMR or EMR Serverless Spark job that writes partitioned feature outputs to an S3 prefix.
4. Keep `dataset_source` and `event_date` as partition columns.
5. Verify point-in-time features and null-rate checks after the job.

## Optional SageMaker-compatible path

1. Use `src/sagemaker_pipeline/pipeline.py` as the local template for Processing, Training, Evaluation, Condition, and RegisterModel steps.
2. Store model metrics and lineage in a model package group.
3. Use approval statuses such as `PendingManualApproval`, `Approved`, or `Rejected` only after validation gates are reviewed.
4. Do not describe this project as a managed SageMaker deployment unless these steps are actually executed in AWS.

## Claim boundary

Default project artifacts are local and compatible templates, not cloud execution evidence.
