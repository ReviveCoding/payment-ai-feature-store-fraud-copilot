from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUTPUTS = ROOT / "outputs"


def read_config() -> dict:
    cfg_path = ROOT / "configs" / "dataset_sources.yaml"
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8"))


def safe_path(value: str | None) -> Path | None:
    if not value:
        return None
    p = Path(value)
    if not p.is_absolute():
        p = ROOT / p
    return p if p.exists() else None


def load_paysim(path: Path, max_rows: int | None) -> pd.DataFrame:
    usecols = ["step", "type", "amount", "nameOrig", "nameDest", "isFraud"]
    df = pd.read_csv(path, usecols=usecols, nrows=max_rows)
    out = pd.DataFrame({
        "dataset_source": "paysim",
        "event_time": pd.to_numeric(df["step"], errors="coerce").fillna(0),
        "amount": pd.to_numeric(df["amount"], errors="coerce").fillna(0),
        "payment_type": df["type"].astype(str),
        "account_id": df["nameOrig"].astype(str),
        "counterparty_id": df["nameDest"].astype(str),
        "label": pd.to_numeric(df["isFraud"], errors="coerce").fillna(0).astype(int),
    })
    return out


def load_baf(path: Path, max_rows: int | None) -> pd.DataFrame:
    header = pd.read_csv(path, nrows=0).columns.tolist()
    keep = [c for c in [
        "fraud_bool", "income", "credit_risk_score", "proposed_credit_limit",
        "customer_age", "device_os", "source", "month"
    ] if c in header]
    df = pd.read_csv(path, usecols=keep, nrows=max_rows)

    amount_col = None
    for c in ["proposed_credit_limit", "income", "credit_risk_score"]:
        if c in df.columns:
            amount_col = c
            break

    event_time = df["month"] if "month" in df.columns else pd.Series(np.arange(len(df)))
    payment_type = df["source"] if "source" in df.columns else "account_opening"
    device = df["device_os"] if "device_os" in df.columns else "unknown"

    out = pd.DataFrame({
        "dataset_source": "baf",
        "event_time": pd.to_numeric(event_time, errors="coerce").fillna(0),
        "amount": pd.to_numeric(df[amount_col], errors="coerce").fillna(0) if amount_col else 1.0,
        "payment_type": payment_type.astype(str),
        "account_id": pd.Series(np.arange(len(df))).astype(str),
        "counterparty_id": device.astype(str),
        "label": pd.to_numeric(df["fraud_bool"], errors="coerce").fillna(0).astype(int),
    })
    return out


def load_ieee(path: Path, max_rows: int | None) -> pd.DataFrame:
    header = pd.read_csv(path, nrows=0).columns.tolist()
    keep = [c for c in [
        "TransactionID", "TransactionDT", "TransactionAmt", "ProductCD",
        "card1", "addr1", "isFraud"
    ] if c in header]
    df = pd.read_csv(path, usecols=keep, nrows=max_rows)

    out = pd.DataFrame({
        "dataset_source": "ieee_cis",
        "event_time": pd.to_numeric(df.get("TransactionDT", pd.Series(np.arange(len(df)))), errors="coerce").fillna(0),
        "amount": pd.to_numeric(df["TransactionAmt"], errors="coerce").fillna(0),
        "payment_type": df.get("ProductCD", "unknown").astype(str),
        "account_id": df.get("card1", pd.Series(np.arange(len(df)))).astype(str),
        "counterparty_id": df.get("addr1", "unknown").astype(str),
        "label": pd.to_numeric(df["isFraud"], errors="coerce").fillna(0).astype(int),
    })
    return out


def add_operational_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["event_time"]).reset_index(drop=True)

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["amount_log"] = np.log1p(np.clip(df["amount"], 0, None))
    df["high_amount_flag"] = (df["amount"] >= df["amount"].quantile(0.95)).astype(int)

    df["account_txn_count_prior"] = df.groupby("account_id").cumcount()
    df["counterparty_txn_count_prior"] = df.groupby("counterparty_id").cumcount()
    df["new_counterparty_flag"] = (df["counterparty_txn_count_prior"] == 0).astype(int)

    account_cumsum = df.groupby("account_id")["amount"].cumsum() - df["amount"]
    prior_count = df["account_txn_count_prior"].replace(0, np.nan)
    df["account_amount_mean_prior"] = (account_cumsum / prior_count).fillna(df["amount"].median())
    df["amount_ratio_to_prior_mean"] = df["amount"] / (df["account_amount_mean_prior"].abs() + 1.0)

    risk_prior_raw = (
        0.35 * df["high_amount_flag"]
        + 0.25 * df["new_counterparty_flag"]
        + 0.20 * (df["amount_ratio_to_prior_mean"] > 3).astype(int)
        + 0.20 * (df["account_txn_count_prior"] <= 1).astype(int)
    )
    df["risk_prior"] = np.clip(risk_prior_raw, 0, 1)
    return df


def temporal_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = df.sort_values("event_time").reset_index(drop=True)
    n = len(df)
    train_end = int(n * 0.60)
    val_end = int(n * 0.80)
    return df.iloc[:train_end].copy(), df.iloc[train_end:val_end].copy(), df.iloc[val_end:].copy()


def build_preprocessor():
    numeric = [
        "event_time", "amount", "amount_log", "high_amount_flag",
        "account_txn_count_prior", "counterparty_txn_count_prior",
        "new_counterparty_flag", "account_amount_mean_prior",
        "amount_ratio_to_prior_mean", "risk_prior",
    ]
    categorical = ["dataset_source", "payment_type"]

    return ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ]), numeric + categorical


def evaluate(y_true, score, amount, capacity: float = 0.05) -> dict:
    y_true = np.asarray(y_true).astype(int)
    score = np.asarray(score)
    amount = np.asarray(amount)

    k = max(1, int(len(y_true) * capacity))
    top_idx = np.argsort(-score)[:k]

    positives = max(1, y_true.sum())
    fraud_loss_total = amount[y_true == 1].sum()
    fraud_loss_top = amount[top_idx][y_true[top_idx] == 1].sum()

    return {
        "rows": int(len(y_true)),
        "positive_rate": float(y_true.mean()),
        "pr_auc": float(average_precision_score(y_true, score)) if len(np.unique(y_true)) > 1 else None,
        "roc_auc": float(roc_auc_score(y_true, score)) if len(np.unique(y_true)) > 1 else None,
        "brier": float(brier_score_loss(y_true, np.clip(score, 0, 1))),
        "precision_at_5pct": float(y_true[top_idx].mean()),
        "recall_at_5pct": float(y_true[top_idx].sum() / positives),
        "review_burden": float(k / len(y_true)),
        "fraud_loss_capture_rate": float(fraud_loss_top / fraud_loss_total) if fraud_loss_total > 0 else 0.0,
        "fraud_loss_captured": float(fraud_loss_top),
        "total_fraud_loss": float(fraud_loss_total),
    }


def fit_models(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame) -> dict:
    pre, features = build_preprocessor()

    X_train, y_train = train[features], train["label"]
    X_val, y_val = val[features], val["label"]
    X_test, y_test = test[features], test["label"]

    models = {
        "logistic_regression": Pipeline([
            ("pre", pre),
            ("clf", LogisticRegression(max_iter=500, class_weight="balanced")),
        ]),
        "hist_gradient_boosting": Pipeline([
            ("pre", pre),
            ("clf", HistGradientBoostingClassifier(max_iter=120, learning_rate=0.07, random_state=42)),
        ]),
    }

    results = {}
    val_scores = {}
    test_scores = {}

    for name, model in models.items():
        t0 = time.time()
        model.fit(X_train, y_train)
        train_seconds = time.time() - t0

        val_score = model.predict_proba(X_val)[:, 1]
        test_score = model.predict_proba(X_test)[:, 1]

        val_metrics = evaluate(y_val, val_score, val["amount"])
        test_metrics = evaluate(y_test, test_score, test["amount"])
        test_metrics["train_seconds"] = train_seconds

        results[name] = {
            "val": val_metrics,
            "test": test_metrics,
        }
        val_scores[name] = val_score
        test_scores[name] = test_score

    best_name = max(
        results.keys(),
        key=lambda n: results[n]["val"]["pr_auc"] if results[n]["val"]["pr_auc"] is not None else -1,
    )

    base_val = val_scores[best_name]
    base_test = test_scores[best_name]

    best_alpha = 0.0
    best_utility = -1e9
    val_prior = val["risk_prior"].to_numpy()
    test_prior = test["risk_prior"].to_numpy()

    for alpha in np.linspace(0, 0.5, 11):
        enhanced_val = np.clip((1 - alpha) * base_val + alpha * val_prior, 0, 1)
        m = evaluate(y_val, enhanced_val, val["amount"])
        utility = (
            (m["pr_auc"] or 0)
            + 0.4 * m["precision_at_5pct"]
            + 0.4 * m["fraud_loss_capture_rate"]
            - 0.2 * m["brier"]
        )
        if utility > best_utility:
            best_utility = utility
            best_alpha = float(alpha)

    enhanced_test = np.clip((1 - best_alpha) * base_test + best_alpha * test_prior, 0, 1)
    enhanced_metrics = evaluate(y_test, enhanced_test, test["amount"])
    enhanced_metrics["selected_alpha_from_validation"] = best_alpha
    enhanced_metrics["base_model"] = best_name

    results["mechanism_informed_enhanced"] = {
        "val_selection_utility": best_utility,
        "test": enhanced_metrics,
    }

    return results


def write_report(dataset: str, mode: str, max_rows: int | None, rows: int, results: dict, runtime_seconds: float):
    REPORTS.mkdir(exist_ok=True)
    OUTPUTS.mkdir(exist_ok=True)

    out_json = OUTPUTS / f"full_benchmark_operational_{dataset}.json"
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")

    md = []
    md.append(f"# Full/Large Benchmark Operational Report: {dataset}\n")
    md.append("## Run Configuration\n")
    md.append(f"- dataset: {dataset}")
    md.append(f"- mode: {mode}")
    md.append(f"- max_rows: {max_rows if max_rows else 'full'}")
    md.append(f"- loaded_rows: {rows}")
    md.append(f"- runtime_seconds: {runtime_seconds:.2f}")
    md.append("- split: temporal 60/20/20 train/validation/test")
    md.append("- claim boundary: public/proxy benchmark only, not JPMC or proprietary bank data\n")

    md.append("## Test Metrics\n")
    md.append("| model | pr_auc | roc_auc | precision_at_5pct | recall_at_5pct | fraud_loss_capture_rate | brier | train_seconds |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for name, block in results.items():
        test = block["test"]
        md.append(
            f"| {name} | {test.get('pr_auc')} | {test.get('roc_auc')} | "
            f"{test.get('precision_at_5pct')} | {test.get('recall_at_5pct')} | "
            f"{test.get('fraud_loss_capture_rate')} | {test.get('brier')} | "
            f"{test.get('train_seconds', '')} |"
        )

    md.append("\n## Interpretation\n")
    md.append("- Baselines show standard fraud-risk model performance under temporal split.")
    md.append("- `mechanism_informed_enhanced` uses validation-selected fusion between the best baseline score and a payment-risk prior.")
    md.append("- This is an operational benchmark extension, not a production deployment or formal model approval.")

    out_md = REPORTS / f"full_benchmark_operational_report_{dataset}.md"
    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "ok",
        "dataset": dataset,
        "rows": rows,
        "report": str(out_md),
        "json": str(out_json),
    }, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["paysim", "baf", "ieee"], required=True)
    parser.add_argument("--max-rows", type=int, default=500000, help="0 means full file")
    args = parser.parse_args()

    cfg = read_config()
    paths = cfg.get("local_optional_paths", {})
    max_rows = None if args.max_rows == 0 else args.max_rows

    t0 = time.time()

    if args.dataset == "paysim":
        path = safe_path(paths.get("paysim_csv"))
        if not path:
            raise FileNotFoundError("paysim_csv not found in configs/dataset_sources.yaml")
        df = load_paysim(path, max_rows)
    elif args.dataset == "baf":
        path = safe_path(paths.get("baf_csv"))
        if not path:
            raise FileNotFoundError("baf_csv not found in configs/dataset_sources.yaml")
        df = load_baf(path, max_rows)
    else:
        path = safe_path(paths.get("ieee_cis_transaction_csv"))
        if not path:
            raise FileNotFoundError("ieee_cis_transaction_csv not found in configs/dataset_sources.yaml")
        df = load_ieee(path, max_rows)

    df = add_operational_features(df)

    if df["label"].sum() == 0:
        raise ValueError("No positive fraud labels found.")

    train, val, test = temporal_split(df)
    results = fit_models(train, val, test)
    runtime = time.time() - t0

    mode = "full" if args.max_rows == 0 else "large_subset"
    write_report(args.dataset, mode, max_rows, len(df), results, runtime)


if __name__ == "__main__":
    main()
