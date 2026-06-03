from __future__ import annotations
import numpy as np
import pandas as pd


def psi(expected, actual, bins: int = 10) -> float:
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    edges = np.quantile(expected, np.linspace(0, 1, bins + 1))
    edges = np.unique(edges)
    if len(edges) < 3:
        return 0.0
    e_counts, _ = np.histogram(expected, bins=edges)
    a_counts, _ = np.histogram(actual, bins=edges)
    e = e_counts / max(1, e_counts.sum()) + 1e-6
    a = a_counts / max(1, a_counts.sum()) + 1e-6
    return float(((a - e) * np.log(a / e)).sum())


def drift_report(train_df: pd.DataFrame, test_df: pd.DataFrame, cols: list[str]) -> dict:
    return {c: psi(train_df[c].values, test_df[c].values) for c in cols if c in train_df and c in test_df}
