from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUTPUTS = ROOT / "outputs"

sys.path.insert(0, str(ROOT))

from scripts.run_operational_benchmark import (  # noqa: E402
    read_config,
    safe_path,
    load_paysim,
    load_baf,
    load_ieee,
    add_operational_features,
    temporal_split,
)


CAPACITIES = [0.01, 0.02, 0.05, 0.10]


def fmt_value(x):
    if x is None:
        return ""
    try:
        if pd.isna(x):
            return ""
    except Exception:
        pass
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


def build_preprocessor():
    numeric = [
        "event_time",
        "amount",
        "amount_log",
        "high_amount_flag",
        "account_txn_count_prior",
        "counterparty_txn_count_prior",
        "new_counterparty_flag",
        "account_amount_mean_prior",
        "amount_ratio_to_prior_mean",
        "risk_prior",
    ]
    categorical = ["dataset_source", "payment_type"]

    pre = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ])

    return pre, numeric + categorical


def make_model(name: str):
    pre, features = build_preprocessor()

    if name == "logistic_regression":
        clf = LogisticRegression(max_iter=500, class_weight="balanced")
    elif name == "hist_gradient_boosting":
        clf = HistGradientBoostingClassifier(
            max_iter=120,
            learning_rate=0.07,
            random_state=42,
        )
    else:
        raise ValueError(f"Unknown model: {name}")

    return Pipeline([("pre", pre), ("clf", clf)]), features


def safe_global_metrics(y_true, score):
    y_true = np.asarray(y_true).astype(int)
    score = np.clip(np.asarray(score), 0, 1)

    out = {
        "pr_auc": None,
        "roc_auc": None,
        "brier": None,
    }

    if len(np.unique(y_true)) > 1:
        out["pr_auc"] = float(average_precision_score(y_true, score))
        out["roc_auc"] = float(roc_auc_score(y_true, score))
        out["brier"] = float(brier_score_loss(y_true, score))

    return out


def capacity_metrics(y_true, score, amount, capacity: float) -> dict:
    y_true = np.asarray(y_true).astype(int)
    score = np.asarray(score)
    amount = np.asarray(amount)

    n = len(y_true)
    k = max(1, int(n * capacity))
    top_idx = np.argsort(-score)[:k]

    true_fraud_count = int(y_true.sum())
    reviewed_fraud_count = int(y_true[top_idx].sum())
    reviewed_count = int(k)

    total_fraud_loss = float(amount[y_true == 1].sum())
    captured_loss = float(amount[top_idx][y_true[top_idx] == 1].sum())

    return {
        "capacity": capacity,
        "top_k": reviewed_count,
        "review_burden": reviewed_count / n,
        "precision_at_capacity": reviewed_fraud_count / reviewed_count if reviewed_count else 0.0,
        "recall_at_capacity": reviewed_fraud_count / true_fraud_count if true_fraud_count else 0.0,
        "fraud_loss_capture_rate": captured_loss / total_fraud_loss if total_fraud_loss > 0 else 0.0,
        "fraud_loss_captured": captured_loss,
        "total_fraud_loss": total_fraud_loss,
        "false_negative_loss": total_fraud_loss - captured_loss,
        "reviewed_fraud_count": reviewed_fraud_count,
        "true_fraud_count": true_fraud_count,
    }


def multi_capacity_utility(y_true, score, amount, capacities=CAPACITIES) -> float:
    global_m = safe_global_metrics(y_true, score)
    cap_rows = [capacity_metrics(y_true, score, amount, c) for c in capacities]

    avg_precision = float(np.mean([r["precision_at_capacity"] for r in cap_rows]))
    avg_recall = float(np.mean([r["recall_at_capacity"] for r in cap_rows]))
    avg_loss_capture = float(np.mean([r["fraud_loss_capture_rate"] for r in cap_rows]))

    pr_auc = global_m["pr_auc"] or 0.0
    brier = global_m["brier"] if global_m["brier"] is not None else 1.0

    return (
        0.35 * pr_auc
        + 0.20 * avg_precision
        + 0.25 * avg_recall
        + 0.25 * avg_loss_capture
        - 0.10 * brier
    )


def load_dataset(dataset: str, max_rows: int | None) -> pd.DataFrame:
    cfg = read_config()
    paths = cfg.get("local_optional_paths", {})

    if dataset == "paysim":
        path = safe_path(paths.get("paysim_csv"))
        if not path:
            raise FileNotFoundError("paysim_csv not found in configs/dataset_sources.yaml")
        return load_paysim(path, max_rows)

    if dataset == "baf":
        path = safe_path(paths.get("baf_csv"))
        if not path:
            raise FileNotFoundError("baf_csv not found in configs/dataset_sources.yaml")
        return load_baf(path, max_rows)

    if dataset == "ieee":
        path = safe_path(paths.get("ieee_cis_transaction_csv"))
        if not path:
            raise FileNotFoundError("ieee_cis_transaction_csv not found in configs/dataset_sources.yaml")
        return load_ieee(path, max_rows)

    raise ValueError(dataset)


def run_capacity_sweep(dataset: str, max_rows: int | None):
    t0 = time.time()

    df = load_dataset(dataset, max_rows)
    df = add_operational_features(df)

    if df["label"].sum() == 0:
        raise ValueError("No positive fraud labels found.")

    train, val, test = temporal_split(df)

    models = ["logistic_regression", "hist_gradient_boosting"]
    val_scores = {}
    test_scores = {}
    results = {}
    train_seconds = {}

    for name in models:
        model, features = make_model(name)

        train_t0 = time.time()
        model.fit(train[features], train["label"])
        train_seconds[name] = time.time() - train_t0

        val_scores[name] = model.predict_proba(val[features])[:, 1]
        test_scores[name] = model.predict_proba(test[features])[:, 1]

        results[name] = {
            "global": safe_global_metrics(test["label"], test_scores[name]),
            "train_seconds": train_seconds[name],
        }

    best_base = max(
        models,
        key=lambda n: safe_global_metrics(val["label"], val_scores[n])["pr_auc"] or -1,
    )

    val_base = val_scores[best_base]
    test_base = test_scores[best_base]
    val_prior = val["risk_prior"].to_numpy()
    test_prior = test["risk_prior"].to_numpy()

    best_alpha = 0.0
    best_utility = -1e18

    for alpha in np.linspace(0.0, 1.0, 21):
        val_enhanced = np.clip((1 - alpha) * val_base + alpha * val_prior, 0, 1)
        utility = multi_capacity_utility(
            val["label"],
            val_enhanced,
            val["amount"],
            capacities=CAPACITIES,
        )
        if utility > best_utility:
            best_utility = utility
            best_alpha = float(alpha)

    test_enhanced = np.clip((1 - best_alpha) * test_base + best_alpha * test_prior, 0, 1)

    enhanced_name = "mechanism_informed_enhanced"
    test_scores[enhanced_name] = test_enhanced
    results[enhanced_name] = {
        "global": safe_global_metrics(test["label"], test_enhanced),
        "selected_alpha_from_validation": best_alpha,
        "base_model": best_base,
        "validation_multi_capacity_utility": best_utility,
    }

    rows = []
    global_rows = []

    for model_name, score in test_scores.items():
        g = safe_global_metrics(test["label"], score)
        global_rows.append({
            "dataset": dataset,
            "model": model_name,
            "rows": int(len(test)),
            "positive_rate": float(test["label"].mean()),
            "pr_auc": g["pr_auc"],
            "roc_auc": g["roc_auc"],
            "brier": g["brier"],
            "train_seconds": train_seconds.get(model_name),
            "selected_alpha": results[model_name].get("selected_alpha_from_validation"),
            "base_model": results[model_name].get("base_model"),
        })

        for cap in CAPACITIES:
            m = capacity_metrics(test["label"], score, test["amount"], cap)
            rows.append({
                "dataset": dataset,
                "model": model_name,
                "capacity_pct": int(cap * 100),
                **m,
                "pr_auc": g["pr_auc"],
                "roc_auc": g["roc_auc"],
                "brier": g["brier"],
            })

    cap_df = pd.DataFrame(rows)
    global_df = pd.DataFrame(global_rows)

    OUTPUTS.mkdir(exist_ok=True)
    REPORTS.mkdir(exist_ok=True)

    cap_csv = OUTPUTS / f"capacity_sweep_{dataset}.csv"
    global_csv = OUTPUTS / f"capacity_sweep_global_{dataset}.csv"
    out_json = OUTPUTS / f"capacity_sweep_{dataset}.json"
    out_md = REPORTS / f"capacity_sweep_report_{dataset}.md"

    cap_df.to_csv(cap_csv, index=False)
    global_df.to_csv(global_csv, index=False)

    runtime = time.time() - t0

    serializable = {
        "dataset": dataset,
        "mode": "full" if max_rows is None else "large_subset",
        "max_rows": "full" if max_rows is None else max_rows,
        "loaded_rows": int(len(df)),
        "test_rows": int(len(test)),
        "runtime_seconds": runtime,
        "capacities": CAPACITIES,
        "best_base_model_by_validation_pr_auc": best_base,
        "selected_alpha_from_validation": best_alpha,
        "global_metrics": global_rows,
        "capacity_sweep": rows,
        "claim_boundary": "Public/proxy benchmark only. Not JPMC data, proprietary bank data, or production approval.",
    }
    out_json.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    md = []
    md.append(f"# Capacity Sweep Operational Report: {dataset}\n")
    md.append("## Run Configuration\n")
    md.append(f"- dataset: {dataset}")
    md.append(f"- mode: {'full' if max_rows is None else 'large_subset'}")
    md.append(f"- max_rows: {'full' if max_rows is None else max_rows}")
    md.append(f"- loaded_rows: {len(df)}")
    md.append(f"- test_rows: {len(test)}")
    md.append(f"- runtime_seconds: {runtime:.2f}")
    md.append("- split: temporal 60/20/20 train/validation/test")
    md.append(f"- best_base_model_by_validation_pr_auc: {best_base}")
    md.append(f"- selected_alpha_from_validation: {best_alpha}")
    md.append("- claim boundary: public/proxy benchmark only, not JPMC or proprietary bank data\n")

    md.append("## Global Ranking / Calibration Metrics\n")
    md.append(df_to_markdown_no_tabulate(global_df))

    md.append("\n## Capacity Sweep Metrics\n")
    display_cols = [
        "dataset",
        "model",
        "capacity_pct",
        "top_k",
        "precision_at_capacity",
        "recall_at_capacity",
        "fraud_loss_capture_rate",
        "false_negative_loss",
        "reviewed_fraud_count",
        "true_fraud_count",
    ]
    md.append(df_to_markdown_no_tabulate(cap_df[display_cols]))

    md.append("\n## Capacity-specific Winners\n")
    for cap_pct in sorted(cap_df["capacity_pct"].unique()):
        sub = cap_df[cap_df["capacity_pct"] == cap_pct]
        md.append(f"\n### Top {cap_pct}% review capacity\n")
        for metric in ["precision_at_capacity", "recall_at_capacity", "fraud_loss_capture_rate"]:
            best = sub.sort_values(metric, ascending=False).iloc[0]
            md.append(f"- Best {metric}: `{best['model']}` = {fmt_value(best[metric])}")

    md.append("\n## Interpretation\n")
    md.append("- This report evaluates operational behavior under limited analyst-review capacity.")
    md.append("- Precision@capacity asks how accurate the review queue is.")
    md.append("- Recall@capacity asks how many fraud events are captured within the review queue.")
    md.append("- Fraud-loss capture asks how much fraud amount is captured within the review queue.")
    md.append("- Do not claim one model is globally best unless it wins the relevant operating metric and capacity range.")
    md.append("- This is not production approval or real bank deployment evidence.")

    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "ok",
        "dataset": dataset,
        "loaded_rows": int(len(df)),
        "test_rows": int(len(test)),
        "report": str(out_md),
        "csv": str(cap_csv),
        "json": str(out_json),
    }, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["paysim", "baf", "ieee"], required=True)
    parser.add_argument("--max-rows", type=int, default=500000, help="0 means full file")
    args = parser.parse_args()

    max_rows = None if args.max_rows == 0 else args.max_rows
    run_capacity_sweep(args.dataset, max_rows)


if __name__ == "__main__":
    main()
