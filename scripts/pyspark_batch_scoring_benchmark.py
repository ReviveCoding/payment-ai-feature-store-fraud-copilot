from __future__ import annotations

import argparse
import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.ml.functions import vector_to_array
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUTPUTS = ROOT / "outputs" / "spark_batch_benchmark"
FEATURE_STORE = ROOT / "data" / "feature_store_spark"
MODEL_REGISTRY = ROOT / "data" / "model_registry"
MODELS = ROOT / "models"


def make_spark(app_name: str) -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.driver.memory", "4g")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .getOrCreate()
    )


def find_paysim_csv() -> Path:
    candidates = list((ROOT / "data" / "raw" / "paysim").glob("*.csv"))
    if not candidates:
        raise FileNotFoundError(
            "No PaySim CSV found under data/raw/paysim. "
            "Expected something like data/raw/paysim/PS_20174392719_1491204439457_log.csv"
        )
    return candidates[0]


def add_features(df):
    required = [
        "step", "type", "amount", "oldbalanceOrg", "newbalanceOrig",
        "oldbalanceDest", "newbalanceDest", "isFraud"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing PaySim columns: {missing}")

    out = (
        df.select(*required)
        .withColumn("step", F.col("step").cast("double"))
        .withColumn("amount", F.col("amount").cast("double"))
        .withColumn("oldbalanceOrg", F.col("oldbalanceOrg").cast("double"))
        .withColumn("newbalanceOrig", F.col("newbalanceOrig").cast("double"))
        .withColumn("oldbalanceDest", F.col("oldbalanceDest").cast("double"))
        .withColumn("newbalanceDest", F.col("newbalanceDest").cast("double"))
        .withColumn("label", F.col("isFraud").cast("double"))
        .withColumn("amount_log", F.log1p(F.col("amount")))
        .withColumn("orig_delta", F.col("oldbalanceOrg") - F.col("newbalanceOrig"))
        .withColumn("dest_delta", F.col("newbalanceDest") - F.col("oldbalanceDest"))
        .withColumn(
            "orig_balance_error",
            F.abs(F.col("oldbalanceOrg") - F.col("amount") - F.col("newbalanceOrig")),
        )
        .withColumn(
            "dest_balance_error",
            F.abs(F.col("oldbalanceDest") + F.col("amount") - F.col("newbalanceDest")),
        )
        .withColumn("zero_orig_before", (F.col("oldbalanceOrg") == 0).cast("double"))
        .withColumn("zero_dest_before", (F.col("oldbalanceDest") == 0).cast("double"))
        .withColumn("high_amount_flag", (F.col("amount") >= 100000).cast("double"))
        .drop("isFraud")
    )
    return out


def temporal_split(df):
    """Stable temporal row-order split.

    PaySim step values can have many ties. On small smoke subsets, quantile-based
    splitting can produce empty validation/test sets. This preserves temporal order
    while forcing non-empty 60/20/20 row partitions.
    """
    ordered = df.orderBy(F.col("step").asc(), F.col("amount").asc())
    n = ordered.count()
    if n < 10:
        raise ValueError(f"Not enough rows for temporal split: n={n}")

    w = Window.orderBy(F.col("step").asc(), F.col("amount").asc())
    indexed = ordered.withColumn("__rn", F.row_number().over(w))

    train_end = int(n * 0.60)
    val_end = int(n * 0.80)

    train = indexed.filter(F.col("__rn") <= train_end).drop("__rn")
    val = indexed.filter((F.col("__rn") > train_end) & (F.col("__rn") <= val_end)).drop("__rn")
    test = indexed.filter(F.col("__rn") > val_end).drop("__rn")

    return train, val, test, train_end, val_end

def add_class_weight(train):
    counts = train.groupBy("label").count().collect()
    count_map = {float(r["label"]): int(r["count"]) for r in counts}
    pos = count_map.get(1.0, 0)
    neg = count_map.get(0.0, 0)
    total = pos + neg

    if pos == 0 or neg == 0:
        raise ValueError(f"Need both classes for training. pos={pos}, neg={neg}")

    pos_weight = total / (2.0 * pos)
    neg_weight = total / (2.0 * neg)

    weighted = train.withColumn(
        "class_weight",
        F.when(F.col("label") == 1.0, F.lit(pos_weight)).otherwise(F.lit(neg_weight)),
    )
    return weighted, {"positive_count": pos, "negative_count": neg, "positive_weight": pos_weight, "negative_weight": neg_weight}


def build_pipeline():
    categorical_cols = ["type"]
    numeric_cols = [
        "step", "amount", "amount_log", "oldbalanceOrg", "newbalanceOrig",
        "oldbalanceDest", "newbalanceDest", "orig_delta", "dest_delta",
        "orig_balance_error", "dest_balance_error", "zero_orig_before",
        "zero_dest_before", "high_amount_flag",
    ]

    type_indexer = StringIndexer(inputCol="type", outputCol="type_idx", handleInvalid="keep")
    type_encoder = OneHotEncoder(inputCol="type_idx", outputCol="type_vec")
    assembler = VectorAssembler(
        inputCols=numeric_cols + ["type_vec"],
        outputCol="features",
        handleInvalid="keep",
    )
    lr = LogisticRegression(
        featuresCol="features",
        labelCol="label",
        weightCol="class_weight",
        probabilityCol="probability",
        rawPredictionCol="rawPrediction",
        maxIter=40,
        regParam=0.01,
        elasticNetParam=0.0,
    )

    return Pipeline(stages=[type_indexer, type_encoder, assembler, lr])


def evaluate_global(scored):
    scored_count = scored.count()
    if scored_count == 0:
        raise ValueError(
            "Scored evaluation dataset is empty. Increase --max-rows or inspect temporal split."
        )

    label_counts = {
        float(r["label"]): int(r["count"])
        for r in scored.groupBy("label").count().collect()
    }

    scored_prob = scored.withColumn("score", vector_to_array("probability")[1])

    brier = (
        scored_prob
        .withColumn("sq_err", F.pow(F.col("label") - F.col("score"), 2))
        .agg(F.avg("sq_err").alias("brier"))
        .collect()[0]["brier"]
    )

    has_both_classes = label_counts.get(0.0, 0) > 0 and label_counts.get(1.0, 0) > 0
    if not has_both_classes:
        return None, None, float(brier), scored_prob

    evaluator_pr = BinaryClassificationEvaluator(
        labelCol="label",
        rawPredictionCol="rawPrediction",
        metricName="areaUnderPR",
    )
    evaluator_roc = BinaryClassificationEvaluator(
        labelCol="label",
        rawPredictionCol="rawPrediction",
        metricName="areaUnderROC",
    )

    pr_auc = evaluator_pr.evaluate(scored)
    roc_auc = evaluator_roc.evaluate(scored)

    return float(pr_auc), float(roc_auc), float(brier), scored_prob

def capacity_metrics(scored_prob, capacities):
    total_rows = scored_prob.count()
    total_fraud = scored_prob.filter(F.col("label") == 1.0).count()
    total_fraud_loss = (
        scored_prob
        .filter(F.col("label") == 1.0)
        .agg(F.sum("amount").alias("loss"))
        .collect()[0]["loss"]
    )
    total_fraud_loss = float(total_fraud_loss or 0.0)

    rows = []
    ordered = scored_prob.orderBy(F.desc("score"))

    for cap in capacities:
        k = max(1, int(total_rows * cap))
        top = ordered.limit(k).cache()

        reviewed_fraud = top.filter(F.col("label") == 1.0).count()
        captured_loss = (
            top
            .filter(F.col("label") == 1.0)
            .agg(F.sum("amount").alias("captured_loss"))
            .collect()[0]["captured_loss"]
        )
        captured_loss = float(captured_loss or 0.0)

        precision = reviewed_fraud / k if k else 0.0
        recall = reviewed_fraud / total_fraud if total_fraud else 0.0
        loss_capture = captured_loss / total_fraud_loss if total_fraud_loss else 0.0

        rows.append({
            "capacity": cap,
            "capacity_pct": int(cap * 100),
            "top_k": k,
            "precision_at_capacity": precision,
            "recall_at_capacity": recall,
            "fraud_loss_capture_rate": loss_capture,
            "fraud_loss_captured": captured_loss,
            "total_fraud_loss": total_fraud_loss,
            "false_negative_loss": total_fraud_loss - captured_loss,
            "reviewed_fraud_count": reviewed_fraud,
            "true_fraud_count": total_fraud,
        })
        top.unpersist()

    return rows


def write_markdown_table(rows, columns):
    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("|" + "|".join(["---"] * len(columns)) + "|")
    for row in rows:
        vals = []
        for c in columns:
            v = row.get(c, "")
            if isinstance(v, float):
                vals.append(f"{v:.6f}")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rows", type=int, default=500000, help="0 means full PaySim file")
    parser.add_argument("--output-tag", type=str, default="paysim_spark_lr")
    args = parser.parse_args()

    REPORTS.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    FEATURE_STORE.mkdir(parents=True, exist_ok=True)
    MODEL_REGISTRY.mkdir(parents=True, exist_ok=True)
    MODELS.mkdir(exist_ok=True)

    started = time.time()
    csv_path = find_paysim_csv()

    spark = make_spark("payment-fraud-risk-pyspark-batch-scoring")

    try:
        raw = spark.read.option("header", "true").option("inferSchema", "true").csv(str(csv_path))
        if args.max_rows and args.max_rows > 0:
            raw = raw.limit(args.max_rows)

        raw_count = raw.count()
        features = add_features(raw).cache()
        feature_count = features.count()
        fraud_count = features.filter(F.col("label") == 1.0).count()

        train, val, test, train_end_row, val_end_row = temporal_split(features)
        train = train.cache()
        val = val.cache()
        test = test.cache()

        train_count = train.count()
        val_count = val.count()
        test_count = test.count()

        train_weighted, class_weight_info = add_class_weight(train)
        val_weighted = val.withColumn("class_weight", F.lit(1.0))
        test_weighted = test.withColumn("class_weight", F.lit(1.0))

        pipeline = build_pipeline()

        train_start = time.time()
        model = pipeline.fit(train_weighted)
        train_seconds = time.time() - train_start

        score_start = time.time()
        scored_test = model.transform(test_weighted).cache()
        scored_count = scored_test.count()
        score_seconds = time.time() - score_start

        pr_auc, roc_auc, brier, scored_prob = evaluate_global(scored_test)

        capacities = [0.01, 0.02, 0.05, 0.10]
        cap_rows = capacity_metrics(scored_prob.cache(), capacities)

        run_id = f"{args.output_tag}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        feature_path = FEATURE_STORE / run_id
        scored_path = OUTPUTS / run_id / "scored_test_parquet"
        model_path = MODELS / f"{run_id}_spark_pipeline_model"

        # Feature-store-style Parquet artifacts
        (
            features
            .write
            .mode("overwrite")
            .partitionBy("type")
            .parquet(str(feature_path))
        )

        # Batch scoring artifact
        (
            scored_prob
            .select(
                "step", "type", "amount", "label", "score",
                "amount_log", "orig_delta", "dest_delta",
                "orig_balance_error", "dest_balance_error",
            )
            .write
            .mode("overwrite")
            .partitionBy("type")
            .parquet(str(scored_path))
        )

        # Spark ML model artifact
        model.write().overwrite().save(str(model_path))

        runtime_seconds = time.time() - started

        metrics = {
            "pr_auc": pr_auc,
            "roc_auc": roc_auc,
            "brier": brier,
            "train_seconds": train_seconds,
            "score_seconds": score_seconds,
            "runtime_seconds": runtime_seconds,
            "raw_rows": raw_count,
            "feature_rows": feature_count,
            "fraud_rows": fraud_count,
            "train_rows": train_count,
            "validation_rows": val_count,
            "test_rows": test_count,
            "scored_rows": scored_count,
            "train_end_row": train_end_row,
            "validation_end_row": val_end_row,
        }

        registry = {
            "model_name": "spark_paysim_fraud_logistic_regression",
            "run_id": run_id,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "framework": "Spark ML / PySpark",
            "problem_type": "payment fraud-risk scoring",
            "dataset": "PaySim public/proxy fraud benchmark",
            "claim_boundary": "Public/proxy benchmark only. Not JPMC data, not proprietary bank data, not production deployment.",
            "training_mode": "local Spark/PySpark batch benchmark",
            "model_path": str(model_path.relative_to(ROOT)),
            "feature_store_path": str(feature_path.relative_to(ROOT)),
            "scored_batch_path": str(scored_path.relative_to(ROOT)),
            "metrics": metrics,
            "capacity_metrics": cap_rows,
            "class_weighting": class_weight_info,
            "registry_status": "REVIEW",
            "sagemaker_compatibility_note": "Local model-registry-style metadata mirrors model version, metrics, artifact paths, approval/review status, and claim-boundary fields; no AWS SageMaker job was executed in this run.",
        }

        registry_path = MODEL_REGISTRY / f"{run_id}_model_registry.json"
        registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

        json_path = OUTPUTS / run_id / "spark_batch_scoring_metrics.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

        report_path = REPORTS / "spark_pyspark_batch_scoring_report.md"

        md = []
        md.append("# Spark/PySpark Batch Scoring Benchmark Report\n")
        md.append("## Run Configuration\n")
        md.append(f"- run_id: {run_id}")
        md.append(f"- source_csv: {csv_path}")
        md.append(f"- max_rows: {'full' if args.max_rows == 0 else args.max_rows}")
        md.append(f"- Spark master: local[*]")
        md.append(f"- Python: {platform.python_version()}")
        md.append(f"- claim boundary: public/proxy benchmark only; not JPMC data, proprietary bank data, or production deployment\n")

        md.append("## Dataset and Split\n")
        split_rows = [
            {"split": "raw_loaded", "rows": raw_count},
            {"split": "features", "rows": feature_count},
            {"split": "fraud_rows", "rows": fraud_count},
            {"split": "train", "rows": train_count},
            {"split": "validation", "rows": val_count},
            {"split": "test", "rows": test_count},
        ]
        md.append(write_markdown_table(split_rows, ["split", "rows"]))

        md.append("\n## Global Test Metrics\n")
        global_rows = [{
            "pr_auc": pr_auc,
            "roc_auc": roc_auc,
            "brier": brier,
            "train_seconds": train_seconds,
            "score_seconds": score_seconds,
            "runtime_seconds": runtime_seconds,
        }]
        md.append(write_markdown_table(
            global_rows,
            ["pr_auc", "roc_auc", "brier", "train_seconds", "score_seconds", "runtime_seconds"],
        ))

        md.append("\n## Capacity Sweep Metrics\n")
        md.append(write_markdown_table(
            cap_rows,
            [
                "capacity_pct", "top_k", "precision_at_capacity", "recall_at_capacity",
                "fraud_loss_capture_rate", "false_negative_loss",
                "reviewed_fraud_count", "true_fraud_count",
            ],
        ))

        md.append("\n## Artifacts\n")
        md.append(f"- feature_store_parquet: `{feature_path.relative_to(ROOT)}`")
        md.append(f"- scored_batch_parquet: `{scored_path.relative_to(ROOT)}`")
        md.append(f"- spark_model_path: `{model_path.relative_to(ROOT)}`")
        md.append(f"- model_registry_json: `{registry_path.relative_to(ROOT)}`")
        md.append(f"- metrics_json: `{json_path.relative_to(ROOT)}`\n")

        md.append("## Resume-Safe Interpretation\n")
        md.append("- This run provides a real local Spark/PySpark execution artifact for batch feature engineering, model training, scoring, Parquet output, and registry-style metadata.")
        md.append("- It does not claim AWS EMR execution, SageMaker training execution, real bank data, JPMC data, or production deployment.")
        md.append("- Use this as supporting evidence for PySpark-compatible distributed processing and feature-store-style batch scoring.\n")

        report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

        readme_path = REPORTS / "spark_execution_artifact_README.md"
        readme = f"""# Spark/PySpark Execution Artifact

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

`{run_id}`
"""
        readme_path.write_text(readme, encoding="utf-8")

        print(json.dumps({
            "status": "ok",
            "run_id": run_id,
            "report": str(report_path),
            "registry": str(registry_path),
            "feature_store": str(feature_path),
            "scored_batch": str(scored_path),
            "model": str(model_path),
            "metrics": metrics,
        }, indent=2))

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
