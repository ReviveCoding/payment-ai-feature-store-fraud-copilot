from __future__ import annotations
from pathlib import Path
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from src.feature_store.point_in_time_join import MODEL_FEATURES
from src.modeling.metrics import evaluate_scores


def temporal_split(df: pd.DataFrame, test_fraction: float = 0.25):
    df = df.sort_values("event_time").reset_index(drop=True)
    cut = int(len(df) * (1 - test_fraction))
    return df.iloc[:cut].copy(), df.iloc[cut:].copy()


def _policy_utility(metrics: dict) -> float:
    """Operating utility used for champion selection in fraud-review settings.

    We keep PR-AUC visible, but do not let it dominate operational metrics. This
    favors models that capture fraud loss within review capacity while remaining
    reasonably calibrated.
    """
    return float(
        0.30 * metrics.get("pr_auc", 0.0)
        + 0.25 * metrics.get("precision_at_capacity", 0.0)
        + 0.30 * metrics.get("fraud_loss_capture_rate", 0.0)
        - 0.15 * metrics.get("ece", 1.0)
    )


def train_vanilla_models(training_set: pd.DataFrame, model_dir: str | Path, test_fraction: float = 0.25, capacity_fraction: float = 0.05) -> dict:
    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    train, test = temporal_split(training_set, test_fraction)
    X_train, y_train = train[MODEL_FEATURES], train["risk_label"].astype(int)
    X_test, y_test = test[MODEL_FEATURES], test["risk_label"].astype(int)
    amount_test = test["amount"].values

    candidates = {
        "logistic_regression": Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=500, class_weight="balanced"))]),
        "random_forest": RandomForestClassifier(n_estimators=120, random_state=42, class_weight="balanced_subsample", min_samples_leaf=3),
        "gradient_boosting": GradientBoostingClassifier(random_state=42),
    }
    # Optional strong tabular fraud baseline. LightGBM is fast on tabular fraud-style
    # data when installed. The demo remains deterministic when it is absent.
    try:
        from lightgbm import LGBMClassifier
        candidates["lightgbm_optional"] = LGBMClassifier(
            n_estimators=80, learning_rate=0.06, num_leaves=31,
            subsample=0.9, colsample_bytree=0.9, class_weight="balanced",
            random_state=42, verbose=-1, n_jobs=2
        )
    except Exception:
        pass

    results = {}
    fitted_models = {}
    scores_by_model = {}
    best_pr_name = None
    best_pr = -1.0
    for name, model in candidates.items():
        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        train_time = time.perf_counter() - t0
        t1 = time.perf_counter()
        score = model.predict_proba(X_test)[:, 1]
        latency_ms = (time.perf_counter() - t1) * 1000 / max(1, len(X_test))
        metrics = evaluate_scores(y_test, score, amount_test, capacity_fraction)
        metrics["train_time_sec"] = float(train_time)
        metrics["p95_latency_ms_proxy"] = float(latency_ms * 1.5)
        metrics["policy_utility"] = _policy_utility(metrics)
        results[name] = metrics
        fitted_models[name] = model
        scores_by_model[name] = score
        if metrics["pr_auc"] > best_pr:
            best_pr = metrics["pr_auc"]
            best_pr_name = name

    # Select operating champion by policy utility, not only by PR-AUC.
    policy_model_name = max(results, key=lambda n: results[n]["policy_utility"])
    policy_model = fitted_models[policy_model_name]
    policy_score = scores_by_model[policy_model_name]

    # Calibrate the operating champion to improve score reliability.
    calibrated = CalibratedClassifierCV(policy_model, cv=3, method="sigmoid")
    calibrated.fit(X_train, y_train)
    cal_score = calibrated.predict_proba(X_test)[:, 1]
    cal_metrics = evaluate_scores(y_test, cal_score, amount_test, capacity_fraction)
    cal_metrics["base_model"] = policy_model_name
    cal_metrics["p95_latency_ms_proxy"] = results[policy_model_name]["p95_latency_ms_proxy"] * 1.2
    cal_metrics["policy_utility"] = _policy_utility(cal_metrics)
    results["calibrated_operating_champion"] = cal_metrics

    # Keep the better of calibrated and raw policy champion for downstream specialty.
    if cal_metrics["policy_utility"] >= results[policy_model_name]["policy_utility"]:
        downstream_score = cal_score
        downstream_name = "calibrated_operating_champion"
        downstream_model = calibrated
        downstream_latency = cal_metrics["p95_latency_ms_proxy"]
    else:
        downstream_score = policy_score
        downstream_name = policy_model_name
        downstream_model = policy_model
        downstream_latency = results[policy_model_name]["p95_latency_ms_proxy"]

    joblib.dump(downstream_model, model_dir / "operating_champion.joblib")
    test_out = test.copy()
    for name, score in scores_by_model.items():
        test_out[f"score_{name}"] = score
    test_out["score_pr_auc_best"] = scores_by_model[best_pr_name]
    test_out["score_policy_best"] = policy_score
    test_out["score_calibrated"] = cal_score
    test_out["score_operating_champion"] = downstream_score
    test_out.to_csv(model_dir / "test_predictions.csv", index=False)
    train.to_csv(model_dir / "train_split.csv", index=False)
    test.to_csv(model_dir / "test_split.csv", index=False)

    champion_metrics = results[downstream_name].copy()
    champion_metrics["champion_score_column"] = "score_operating_champion"
    results["selected_operating_champion"] = champion_metrics

    return {
        "results": results,
        "best_model_name": downstream_name,
        "best_pr_auc_model_name": best_pr_name,
        "policy_model_name": policy_model_name,
        "model_path": str(model_dir / "operating_champion.joblib"),
        "test_predictions_path": str(model_dir / "test_predictions.csv"),
        "train_split_path": str(model_dir / "train_split.csv"),
        "test_split_path": str(model_dir / "test_split.csv"),
        "feature_names": MODEL_FEATURES,
    }
