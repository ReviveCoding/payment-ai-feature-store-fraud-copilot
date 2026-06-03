from __future__ import annotations
import json
from pathlib import Path


def build_sagemaker_compatible_pipeline_spec(out_path: str | Path) -> dict:
    spec = {
        "pipeline_name": "payment-fraud-risk-local-compatible-pipeline",
        "execution_mode": "local_sagemaker_compatible_template",
        "steps": [
            {"name": "ProcessingStep", "purpose": "PySpark-compatible feature generation and validation"},
            {"name": "TrainingStep", "purpose": "train vanilla and improved fraud-risk models"},
            {"name": "EvaluationStep", "purpose": "compute PR-AUC, Precision@K, calibration, fraud-loss capture"},
            {"name": "ConditionStep", "purpose": "apply release gates"},
            {"name": "RegisterModel", "purpose": "write local model package metadata with approval status"},
        ],
    }
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return spec
