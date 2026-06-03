from __future__ import annotations
import importlib.util
import time
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score


def run_transformer_routing_smoke(cfpb_df: pd.DataFrame, out_path: str | Path | None = None) -> dict:
    """Run a lightweight NLP routing smoke test for CFPB-style narratives.

    The function is intentionally offline-safe. If Hugging Face Transformers is not
    installed or no local model is available, it falls back to a TF-IDF logistic classifier
    while still documenting the transformer readiness boundary.
    """
    out_path = Path(out_path) if out_path else None
    df = cfpb_df.copy()
    if "narrative" not in df.columns:
        return {"status": "SKIPPED", "reason": "narrative column not found", "transformers_available": bool(importlib.util.find_spec("transformers"))}
    label_col = "issue" if "issue" in df.columns else "severity" if "severity" in df.columns else None
    if label_col is None or df[label_col].nunique() < 2:
        return {"status": "SKIPPED", "reason": "no multi-class routing label found", "transformers_available": bool(importlib.util.find_spec("transformers"))}
    n = len(df)
    test_size = 0.30 if n >= 50 else 0.25
    train, test = train_test_split(df, test_size=test_size, random_state=42, stratify=df[label_col] if df[label_col].nunique() > 1 else None)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=2000)
    X_train = vectorizer.fit_transform(train["narrative"].astype(str))
    X_test = vectorizer.transform(test["narrative"].astype(str))
    model = LogisticRegression(max_iter=300, class_weight="balanced")
    t0 = time.perf_counter()
    model.fit(X_train, train[label_col].astype(str))
    train_time = time.perf_counter() - t0
    pred = model.predict(X_test)
    metrics = {
        "status": "PASS",
        "mode": "tfidf_logistic_fallback",
        "transformers_available": bool(importlib.util.find_spec("transformers")),
        "label": label_col,
        "rows": int(n),
        "classes": sorted(df[label_col].astype(str).unique().tolist()),
        "accuracy": float(accuracy_score(test[label_col].astype(str), pred)),
        "macro_f1": float(f1_score(test[label_col].astype(str), pred, average="macro", zero_division=0)),
        "train_time_sec": float(train_time),
        "claim_boundary": "This is an offline NLP routing smoke test. It is not a production LLM/fine-tuning run. If transformers/local model weights are available, this module can be extended to DistilBERT/MiniLM fine-tuning.",
    }
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"true": test[label_col].astype(str).values, "pred": pred}).to_csv(out_path, index=False)
    return metrics
