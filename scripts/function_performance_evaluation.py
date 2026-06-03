from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
MODEL_REGISTRY = ROOT / "data" / "model_registry" / "model_package.json"

CORE_REPORTS = [
    "feature_store_validation_report.md",
    "baseline_vs_specialty_ablation_report.md",
    "model_selection_report.md",
    "kpi_policy_readout.md",
    "release_decision.md",
    "data_quality_and_backfill_report.md",
    "model_monitoring_baseline_report.md",
    "drift_monitoring_report.md",
    "explainability_report.md",
    "batch_scoring_contract_report.md",
]

PERFORMANCE_TERMS = [
    "pr_auc", "PR-AUC", "precision", "Precision",
    "recall", "Recall", "fraud_loss", "loss_capture",
    "ECE", "Brier", "latency", "review", "REVIEW",
    "PASS", "BLOCK", "release", "decision",
    "baseline", "calibrated", "residual", "envelope",
]

def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")

def extract_lines(text: str, limit: int = 30) -> list[str]:
    lines = []
    for line in text.splitlines():
        clean = line.strip()
        if clean and any(term in clean for term in PERFORMANCE_TERMS):
            lines.append(clean)
        if len(lines) >= limit:
            break
    return lines

def main() -> int:
    REPORTS.mkdir(exist_ok=True)

    present = {name: (REPORTS / name).exists() for name in CORE_REPORTS}
    present_count = sum(present.values())

    release_text = read_text(REPORTS / "release_decision.md")
    ablation_text = read_text(REPORTS / "baseline_vs_specialty_ablation_report.md")
    feature_text = read_text(REPORTS / "feature_store_validation_report.md")
    quality_text = read_text(REPORTS / "data_quality_and_backfill_report.md")

    checks = {
        "core_reports_present": f"{present_count}/{len(CORE_REPORTS)}",
        "model_registry_present": MODEL_REGISTRY.exists(),
        "release_decision_detected": any(x in release_text for x in ["PASS", "REVIEW", "BLOCK"]),
        "ablation_metrics_detected": any(x in ablation_text for x in ["PR-AUC", "pr_auc", "precision", "fraud_loss", "ECE", "Brier"]),
        "feature_store_validation_detected": any(x in feature_text for x in ["feature", "point", "parity", "validation", "PASS"]),
        "data_quality_checks_detected": any(x in quality_text for x in ["null", "duplicate", "idempotence", "PASS"]),
    }

    blocking = []
    if present_count < len(CORE_REPORTS):
        blocking.append("Some core reports are missing.")
    if not checks["model_registry_present"]:
        blocking.append("Model registry artifact is missing.")
    if not checks["release_decision_detected"]:
        blocking.append("Release decision was not detected.")
    if not checks["ablation_metrics_detected"]:
        blocking.append("Ablation/performance metrics were not detected.")

    status = "PASS" if not blocking else "REVIEW"

    md = []
    md.append("# Function and Performance Evaluation Report\n")
    md.append("## Summary\n")
    md.append(f"- Status: **{status}**")
    for k, v in checks.items():
        md.append(f"- {k}: {v}")

    md.append("\n## Core Report Availability\n")
    for name, ok in present.items():
        md.append(f"- {name}: {'PASS' if ok else 'MISSING'}")

    md.append("\n## Performance Evidence Extracts\n")
    for name in [
        "baseline_vs_specialty_ablation_report.md",
        "model_selection_report.md",
        "kpi_policy_readout.md",
        "release_decision.md",
        "drift_monitoring_report.md",
        "model_monitoring_baseline_report.md",
        "explainability_report.md",
        "batch_scoring_contract_report.md",
    ]:
        text = read_text(REPORTS / name)
        md.append(f"\n### {name}\n")
        if not text:
            md.append("- MISSING")
            continue
        lines = extract_lines(text)
        if not lines:
            md.append("- No metric keyword lines detected. Open this report manually.")
        else:
            for line in lines:
                md.append(f"- {line}")

    md.append("\n## Verdict\n")
    if blocking:
        md.append("- Items to review:")
        for item in blocking:
            md.append(f"  - {item}")
    else:
        md.append("- Core functional and performance evidence is present.")

    summary = {
        "status": status,
        "checks": checks,
        "blocking_items": blocking,
        "core_reports": present,
    }

    (REPORTS / "function_performance_evaluation_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (REPORTS / "function_performance_evaluation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report": "reports/function_performance_evaluation_report.md",
        "summary": "reports/function_performance_evaluation_summary.json",
        "blocking_items": blocking,
    }, indent=2))

    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
