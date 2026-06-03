from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
REPORTS = ROOT / "reports"

def fmt_value(x):
    if pd.isna(x):
        return ""
    if isinstance(x, float):
        return f"{x:.6f}"
    return str(x)

def df_to_markdown_no_tabulate(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = []
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "|".join(["---"] * len(cols)) + "|")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt_value(row[c]) for c in cols) + " |")
    return "\n".join(lines)

datasets = ["paysim", "baf", "ieee"]
rows = []

for ds in datasets:
    p = OUTPUTS / f"full_benchmark_operational_{ds}.json"
    if not p.exists():
        continue

    data = json.loads(p.read_text(encoding="utf-8"))

    for model, block in data.items():
        test = block.get("test", {})
        rows.append({
            "dataset": ds,
            "model": model,
            "rows": test.get("rows"),
            "positive_rate": test.get("positive_rate"),
            "pr_auc": test.get("pr_auc"),
            "roc_auc": test.get("roc_auc"),
            "precision_at_5pct": test.get("precision_at_5pct"),
            "recall_at_5pct": test.get("recall_at_5pct"),
            "fraud_loss_capture_rate": test.get("fraud_loss_capture_rate"),
            "brier": test.get("brier"),
            "train_seconds": test.get("train_seconds"),
            "selected_alpha": test.get("selected_alpha_from_validation"),
            "base_model": test.get("base_model"),
        })

df = pd.DataFrame(rows)

REPORTS.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

summary_csv = OUTPUTS / "full_benchmark_operational_summary.csv"
summary_md = REPORTS / "full_benchmark_operational_summary.md"

df.to_csv(summary_csv, index=False)

md = []
md.append("# Full Benchmark Operational Summary\n")
md.append("This report aggregates PaySim full and BAF/IEEE large-subset operational benchmark results.\n")
md.append(df_to_markdown_no_tabulate(df))
md.append("\n## Interpretation\n")
md.append("- Do not claim the enhanced method wins every metric.")
md.append("- Use metric-specific claims: review-capacity recall/precision, PR-AUC, fraud-loss capture, and calibration can have different winners.")
md.append("- This is public/proxy benchmark evidence, not JPMC or proprietary bank production evidence.\n")

if not df.empty:
    for ds in df["dataset"].unique():
        sub = df[df["dataset"] == ds]
        md.append(f"## {ds} metric winners\n")

        for metric in ["pr_auc", "roc_auc", "precision_at_5pct", "recall_at_5pct", "fraud_loss_capture_rate"]:
            valid = sub.dropna(subset=[metric])
            if valid.empty:
                md.append(f"- Best {metric}: unavailable")
                continue
            best = valid.sort_values(metric, ascending=False).iloc[0]
            md.append(f"- Best {metric}: `{best['model']}` = {fmt_value(best[metric])}")

        valid_brier = sub.dropna(subset=["brier"])
        if valid_brier.empty:
            md.append("- Best brier: unavailable\n")
        else:
            best_brier = valid_brier.sort_values("brier", ascending=True).iloc[0]
            md.append(f"- Best brier: `{best_brier['model']}` = {fmt_value(best_brier['brier'])}\n")

summary_md.write_text("\n".join(md), encoding="utf-8")

print(df)
print(f"\nWrote {summary_md}")
print(f"Wrote {summary_csv}")
