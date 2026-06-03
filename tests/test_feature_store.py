from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_generation.generate_sample_data import generate_public_style_fraud_sample
from src.spark_jobs.build_payment_features import build_features
from src.feature_store.offline_store import write_partitioned_offline_store, read_offline_store
from src.feature_store.online_lookup import build_online_store
from src.feature_store.parity_checks import offline_online_parity


def test_offline_online_feature_store(tmp_path):
    df = build_features(generate_public_style_fraud_sample(n=120, seed=4))
    manifest = write_partitioned_offline_store(df, tmp_path / "offline")
    assert manifest["rows"] == 120
    loaded = read_offline_store(tmp_path / "offline")
    assert len(loaded) == 120
    meta = build_online_store(df, tmp_path / "online.sqlite")
    assert meta["rows"] > 0
    parity = offline_online_parity(df, str(tmp_path / "online.sqlite"))
    assert parity["parity_pass"] is True
