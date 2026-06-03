from __future__ import annotations


def _utility(metrics: dict) -> float:
    return float(
        0.30 * metrics.get("pr_auc", 0.0)
        + 0.25 * metrics.get("precision_at_capacity", 0.0)
        + 0.30 * metrics.get("fraud_loss_capture_rate", 0.0)
        - 0.15 * metrics.get("ece", 1.0)
    )


def evaluate_release_gates(final_metrics: dict, baseline_metrics: dict, gates: dict) -> dict:
    """Evaluate local release gates for the reference framework.

    PASS means all hard gates pass. REVIEW means the candidate is operationally
    plausible but needs human approval. BLOCK is reserved for bad calibration,
    latency failure, or utility regression.
    """
    g = gates.get("release_gates", gates)
    checks = {}
    checks["pr_auc_lift"] = final_metrics.get("pr_auc", 0) - baseline_metrics.get("pr_auc", 0)
    checks["precision_at_5pct_lift"] = final_metrics.get("precision_at_capacity", 0) - baseline_metrics.get("precision_at_capacity", 0)
    checks["loss_capture_lift"] = final_metrics.get("fraud_loss_capture_rate", 0) - baseline_metrics.get("fraud_loss_capture_rate", 0)
    checks["ece"] = final_metrics.get("ece", 1)
    checks["p95_latency_ms"] = final_metrics.get("p95_latency_ms_proxy", 50)
    checks["utility_lift"] = _utility(final_metrics) - _utility(baseline_metrics)
    pass_flags = {
        "pr_auc_lift": checks["pr_auc_lift"] >= g.get("min_pr_auc_lift_vs_baseline", 0),
        "precision_lift": checks["precision_at_5pct_lift"] >= g.get("min_precision_at_5pct_lift_vs_baseline", 0),
        "loss_capture_lift": checks["loss_capture_lift"] >= g.get("min_loss_capture_lift_vs_baseline", 0),
        "ece": checks["ece"] <= g.get("max_ece", 1),
        "latency": checks["p95_latency_ms"] <= g.get("max_p95_latency_ms", 999999),
        "utility_lift": checks["utility_lift"] >= -0.005,
    }
    if all(pass_flags.values()):
        decision = "PASS"
    elif pass_flags["ece"] and pass_flags["latency"] and pass_flags["utility_lift"]:
        decision = "REVIEW"
    else:
        decision = "BLOCK"
    return {"decision": decision, "checks": checks, "pass_flags": pass_flags}
