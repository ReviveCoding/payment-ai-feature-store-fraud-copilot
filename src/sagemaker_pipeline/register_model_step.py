from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from src.utils import write_json


def register_local_model_package(out_path: str | Path, model_path: str, metrics: dict, approval_status: str, feature_names: list[str], governance_artifacts: dict | None = None) -> dict:
    package = {
        "model_package_group_name": "payment-fraud-risk-models",
        "model_version": "1.0.0-local",
        "model_artifact": model_path,
        "approval_status": approval_status,
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "feature_names": feature_names,
        "lineage": {
            "data": "public-style/synthetic sample mode",
            "feature_store": "local partitioned offline store with online SQLite lookup",
            "training_pipeline": "SageMaker-compatible local template",
        },
        "governance_artifacts": governance_artifacts or {},
        "monitoring_plan": {
            "data_quality_baseline": (governance_artifacts or {}).get("monitoring_baseline"),
            "feature_importance": (governance_artifacts or {}).get("feature_importance"),
            "batch_scoring_sample": (governance_artifacts or {}).get("batch_scoring_sample"),
            "recommended_review_cadence": "recompute drift, calibration, and review-capacity metrics before any production promotion",
        },
        "claim_boundary": "Not a production SageMaker registration unless explicitly run on AWS.",
    }
    write_json(out_path, package)
    return package
