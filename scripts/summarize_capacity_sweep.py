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

dfs = []
for ds in ["paysim", "baf", "ieee"]:
    p = OUTPUTS / f"capacity_sweep_{ds}.csv"
    if p.exists():
        dfs.append(pd.read_csv(p))

if not dfs:
    raise FileNotFoundError("No capacity_sweep_*.csv files found in outputs/")

df = pd.concat(dfs, ignore_index=True)
summary_csv = OUTPUTS / "capacity_sweep_summary.csv"
summary_md = REPORTS / "capacity_sweep_summary.md"

df.to_csv(summary_csv, index=False)

md = []
md.append("# Capacity Sweep Summary\n")
md.append("This report aggregates Top 1%, 2%, 5%, and 10% review-capacity results across public/proxy benchmarks.\n")

winner_rows = []
for ds in df["dataset"].unique():
    for cap in sorted(df["capacity_pct"].unique()):
        sub = df[(df["dataset"] == ds) & (df["capacity_pct"] == cap)]
        if sub.empty:
            continue
        for metric in ["precision_at_capacity", "recall_at_capacity", "fraud_loss_capture_rate"]:
            best = sub.sort_values(metric, ascending=False).iloc[0]
            winner_rows.append({
                "dataset": ds,
                "capacity_pct": cap,
                "metric": metric,
                "winner": best["model"],
                "value": best[metric],
            })

winner_df = pd.DataFrame(winner_rows)

md.append("## Capacity-specific Winners\n")
md.append(df_to_markdown_no_tabulate(winner_df))

md.append("\n## Full Capacity Sweep Table\n")
display_cols = [
    "dataset",
    "model",
    "capacity_pct",
    "precision_at_capacity",
    "recall_at_capacity",
    "fraud_loss_capture_rate",
    "false_negative_loss",
]
md.append(df_to_markdown_no_tabulate(df[display_cols]))

md.append("\n## Interpretation\n")
md.append("- This is the most operationally relevant comparison because analyst capacity changes the best model choice.")
md.append("- Use metric-specific claims rather than claiming one method dominates every dataset and capacity.")
md.append("- This is public/proxy benchmark evidence only, not JPMC or proprietary bank production evidence.")

summary_md.write_text("\n".join(md) + "\n", encoding="utf-8")

print(f"Wrote {summary_md}")
print(f"Wrote {summary_csv}")
print(winner_df)
