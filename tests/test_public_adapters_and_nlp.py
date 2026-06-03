from pathlib import Path
import pandas as pd
from src.adapters.public_benchmark_adapters import load_paysim, load_baf, load_ieee_cis
from src.data_generation.generate_sample_data import generate_cfpb_style_sample
from src.nlp.transformer_text_routing import run_transformer_routing_smoke


def test_public_dataset_adapters(tmp_path):
    paysim = tmp_path / "paysim.csv"
    pd.DataFrame({"step": [1, 2], "type": ["TRANSFER", "CASH_OUT"], "amount": [100.0, 500.0], "nameOrig": ["A", "B"], "nameDest": ["C", "D"], "isFraud": [0, 1]}).to_csv(paysim, index=False)
    assert set(["event_id", "amount", "risk_label"]).issubset(load_paysim(paysim).columns)

    baf = tmp_path / "baf.csv"
    pd.DataFrame({"fraud_bool": [0, 1], "income": [0.1, 0.9], "device_os": ["windows", "linux"]}).to_csv(baf, index=False)
    assert load_baf(baf)["risk_label"].sum() == 1

    ieee = tmp_path / "ieee.csv"
    pd.DataFrame({"TransactionID": [1, 2], "TransactionAmt": [10, 20], "isFraud": [0, 1], "card1": [111, 222]}).to_csv(ieee, index=False)
    assert load_ieee_cis(ieee)["amount"].sum() == 30


def test_nlp_routing_smoke():
    df = generate_cfpb_style_sample(n=80)
    result = run_transformer_routing_smoke(df)
    assert result["status"] == "PASS"
    assert "macro_f1" in result
