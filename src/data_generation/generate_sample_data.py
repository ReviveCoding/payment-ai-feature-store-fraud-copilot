from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def generate_public_style_fraud_sample(n: int = 2500, seed: int = 42) -> pd.DataFrame:
    """Generate public-style payment fraud records for demo execution.

    This is not real bank data. Labels are generated from transparent fraud-risk mechanisms
    so that residual correction, review-capacity metrics, and release gates can be tested.
    """
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2025-01-01")
    event_time = start + pd.to_timedelta(rng.integers(0, 60 * 24 * 60, n), unit="m")
    dataset_source = rng.choice(["paysim_style_sample", "baf_style_sample"], size=n, p=[0.55, 0.45])
    account = rng.integers(1, max(30, n // 18), n)
    counterparty = rng.integers(1, max(40, n // 12), n)
    device = rng.integers(1, max(20, n // 25), n)
    countries = np.array(["US", "GB", "FR", "BR", "NG", "SG", "MX", "CA"])
    debtor_country = rng.choice(countries, n, p=[.42,.12,.08,.07,.06,.09,.08,.08])
    creditor_country = rng.choice(countries, n, p=[.44,.10,.08,.08,.05,.10,.07,.08])
    cross_border = (debtor_country != creditor_country).astype(int)
    channel = rng.choice(["web", "mobile", "api", "branch"], n, p=[.32,.44,.20,.04])
    payment_type = rng.choice(["credit_transfer", "wallet_transfer", "bill_pay", "merchant_payment"], n)
    base_amount = rng.lognormal(mean=6.5, sigma=1.0, size=n)
    # Generate rare high values for suspicious activity
    spike = rng.binomial(1, 0.08, n)
    amount = np.round(base_amount * (1 + spike * rng.uniform(2.0, 8.0, n)), 2)
    device_age = rng.integers(0, 180, n)
    new_device = (device_age <= 3).astype(int)
    high_risk_corridor = np.isin(debtor_country + ">" + creditor_country, ["US>NG", "GB>NG", "US>BR", "MX>NG"]).astype(int)
    processing_time = rng.gamma(shape=2.0, scale=3.0, size=n).round(2)
    rejected_flag = rng.binomial(1, 0.04 + 0.12 * high_risk_corridor + 0.05 * new_device).clip(0,1)

    # Mechanism-informed latent risk controls true labels but leaves residual noise.
    z = (
        -4.2
        + 0.00045 * np.minimum(amount, 10000)
        + 0.95 * new_device
        + 0.85 * high_risk_corridor
        + 0.55 * cross_border
        + 0.45 * rejected_flag
        + 0.35 * spike
        + rng.normal(0, 0.75, n)
    )
    prob = _sigmoid(z)
    risk_label = rng.binomial(1, prob)
    # Add a few more positives in high amount tails to make cost-sensitive metrics meaningful.
    tail = amount > np.quantile(amount, 0.97)
    risk_label = np.where(tail & (rng.random(n) < 0.25), 1, risk_label)

    fraud_type = np.where(risk_label == 0, "none", rng.choice(["account_takeover_proxy", "transaction_fraud_proxy", "promotion_abuse_proxy"], n))
    status = np.where(rejected_flag == 1, rng.choice(["RJCT", "PDNG"], n), "ACSP")
    failure_reason = np.where(rejected_flag == 1, rng.choice(["AC01", "AM04", "FRAD", "RR04"], n), "")

    df = pd.DataFrame({
        "dataset_source": dataset_source,
        "event_id": [f"EVT-{i:07d}" for i in range(n)],
        "event_time": event_time,
        "account_id_hash": [f"acct_{x:05d}" for x in account],
        "customer_id_hash": [f"cust_{x:05d}" for x in account],
        "device_id_hash": [f"dev_{x:05d}" for x in device],
        "counterparty_id_hash": [f"cp_{x:05d}" for x in counterparty],
        "amount": amount,
        "currency": rng.choice(["USD", "GBP", "EUR"], n, p=[.72,.12,.16]),
        "channel": channel,
        "payment_type": payment_type,
        "payment_status": status,
        "failure_reason": failure_reason,
        "fraud_type_proxy": fraud_type,
        "risk_label": risk_label.astype(int),
        "debtor_country": debtor_country,
        "creditor_country": creditor_country,
        "processing_time_secs": processing_time,
        "purpose_code": rng.choice(["SUPP", "SALA", "TAXS", "LOAN", "GDDS"], n),
        "source_file": "generated_public_style_sample",
    }).sort_values("event_time").reset_index(drop=True)
    return df


def generate_cfpb_style_sample(n: int = 120, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    products = ["Checking or savings account", "Money transfer", "Credit card", "Debt collection"]
    issues = ["unauthorized transaction", "transfer delay", "account access", "incorrect fee", "fraud alert"]
    narratives = []
    for i in range(n):
        product = rng.choice(products)
        issue = rng.choice(issues)
        severity = rng.choice(["low", "medium", "high"], p=[.45,.35,.20])
        text = f"Consumer reported {issue} involving {product}. Evidence includes transaction timing, account activity, and company response. Severity appears {severity}."
        narratives.append((product, issue, severity, text))
    return pd.DataFrame(narratives, columns=["product", "issue", "severity", "narrative"]).assign(complaint_id=lambda x: [f"CFPB-{i:05d}" for i in range(len(x))])


def save_samples(out_dir: str | Path, n: int = 2500) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    generate_public_style_fraud_sample(n=n).to_csv(out_dir / "public_style_fraud_sample.csv", index=False)
    generate_cfpb_style_sample().to_csv(out_dir / "cfpb_style_narratives.csv", index=False)
