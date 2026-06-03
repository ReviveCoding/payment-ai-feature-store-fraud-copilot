from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "Makefile",
    "CLAIM_BOUNDARIES.md",
    "configs/dataset_sources.yaml",
    "scripts/run_demo.py",
    "scripts/generate_reports.py",
    "scripts/local_runnable_audit.py",
    "reports/feature_store_validation_report.md",
    "reports/baseline_vs_specialty_ablation_report.md",
    "reports/release_decision.md",
    "data/model_registry/model_package.json",
]

def exists(path: str) -> bool:
    return (ROOT / path).exists()

def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        shell=False,
    )
    return p.returncode, (p.stdout + "\n" + p.stderr).strip()

def main() -> int:
    missing = [p for p in REQUIRED_FILES if not exists(p)]

    audit_code, audit_output = run([sys.executable, "scripts/local_runnable_audit.py"])

    raw_data_present = (ROOT / "data" / "raw").exists()
    raw_large_files = []
    raw_dir = ROOT / "data" / "raw"
    if raw_dir.exists():
        for f in raw_dir.rglob("*"):
            if f.is_file() and f.stat().st_size > 25 * 1024 * 1024:
                raw_large_files.append(str(f.relative_to(ROOT)))

    status = "PASS"
    notes = []

    if missing:
        status = "FAIL"
        notes.append("Required project files are missing.")

    if audit_code != 0:
        status = "FAIL"
        notes.append("local_runnable_audit.py returned a nonzero code.")

    if raw_large_files:
        notes.append(
            "Large raw datasets are present locally. This is acceptable for local benchmarking, "
            "but data/raw must remain ignored and must not be committed to GitHub."
        )

    result = {
        "status": status,
        "missing_required_files": missing,
        "audit_code": audit_code,
        "raw_data_present": raw_data_present,
        "large_raw_files_count": len(raw_large_files),
        "large_raw_files_preview": raw_large_files[:10],
        "notes": notes,
    }

    out_dir = ROOT / "reports"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "final_verification_results.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )
    (out_dir / "final_verification_results.md").write_text(
        "# Final Verification Results\n\n"
        f"- Status: **{status}**\n"
        f"- Missing required files: {len(missing)}\n"
        f"- Audit return code: {audit_code}\n"
        f"- Raw data present: {raw_data_present}\n"
        f"- Large raw files count: {len(raw_large_files)}\n\n"
        "## Notes\n"
        + "\n".join(f"- {n}" for n in notes)
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(result, indent=2))
    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
