from __future__ import annotations
from pathlib import Path
import pandas as pd
from src.data_generation.generate_sample_data import generate_cfpb_style_sample


def load_or_generate_cfpb_sample(path: str | Path | None = None) -> pd.DataFrame:
    # .7z extraction is intentionally not required for demo reproducibility.
    if path and Path(path).exists() and Path(path).suffix.lower() == ".csv":
        df = pd.read_csv(path)
        narrative_col = "Consumer complaint narrative" if "Consumer complaint narrative" in df.columns else None
        if narrative_col:
            return df[[narrative_col]].rename(columns={narrative_col: "narrative"}).dropna().head(500)
    return generate_cfpb_style_sample()
