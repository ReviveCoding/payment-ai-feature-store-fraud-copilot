from __future__ import annotations
from pathlib import Path
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "CLAIM_BOUNDARIES.md",
    "Makefile",
    "requirements.txt",
    "pyproject.toml",
    ".github/workflows/local-ci.yml",
    "configs/canonical_schema.yaml",
    "configs/feature_groups.yaml",
    "configs/release_gates.yaml",
    "src/spark_jobs/build_payment_features.py",
    "src/feature_store/point_in_time_join.py",
    "src/modeling/train_models.py",
    "src/sagemaker_pipeline/pipeline.py",
    "reports/feature_store_validation_report.md",
    "reports/baseline_vs_specialty_ablation_report.md",
    "reports/validation_memo.md",
    "reports/release_decision.md",
    "reports/data_quality_and_backfill_report.md",
    "reports/model_monitoring_baseline_report.md",
    "reports/explainability_report.md",
    "reports/batch_scoring_contract_report.md",
]

FORBIDDEN_NAMES = {".env", "credentials", "aws_credentials", "id_rsa", "secret"}
FORBIDDEN_CACHE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def run_audit() -> dict:
    missing = [p for p in REQUIRED_FILES if not (ROOT / p).exists()]
    suspicious = []
    large_files = []
    cache_dirs = []
    for p in ROOT.rglob("*"):
        rel = str(p.relative_to(ROOT))
        if p.is_dir() and p.name in FORBIDDEN_CACHE_DIRS:
            cache_dirs.append(rel)
        if p.is_file():
            if any(tok in p.name.lower() for tok in FORBIDDEN_NAMES):
                suspicious.append(rel)
            if p.stat().st_size > 25 * 1024 * 1024:
                large_files.append({"path": rel, "size_mb": round(p.stat().st_size / (1024 * 1024), 2)})
    ci_file = ROOT / ".github" / "workflows" / "local-ci.yml"
    ci_text = ci_file.read_text(encoding="utf-8") if ci_file.exists() else ""
    ci_checks = {
        "run_demo": "make run-demo" in ci_text,
        "test": "make test" in ci_text,
        "reports": "make reports" in ci_text,
        "audit": "make audit" in ci_text or "local_runnable_audit.py" in ci_text,
    }
    report = {
        "status": "PASS" if not missing and not suspicious and not large_files and all(ci_checks.values()) else "REVIEW",
        "missing_required_files": missing,
        "suspicious_secret_like_files": suspicious,
        "large_files_over_25mb": large_files,
        "cache_directories_present_warning_only": cache_dirs,
        "github_actions_checks": ci_checks,
        "github_runnable_commands": ["make run-demo", "make test", "make reports", "make audit", "make verify"],
        "claim_boundary_present": (ROOT / "CLAIM_BOUNDARIES.md").exists(),
    }
    out = ROOT / "reports" / "local_github_runnable_audit.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("# Local / GitHub Runnable Audit\n\n```json\n" + json.dumps(report, indent=2) + "\n```\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = run_audit()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "PASS" else 1)
