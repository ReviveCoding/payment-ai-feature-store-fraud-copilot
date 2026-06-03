from __future__ import annotations
from pathlib import Path
import json
import pandas as pd


def write_partitioned_offline_store(features: pd.DataFrame, out_dir: str | Path) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"format": None, "partitions": [], "rows": int(len(features))}
    engine = None
    try:
        import pyarrow  # noqa: F401
        engine = "pyarrow"
    except Exception:
        try:
            import fastparquet  # noqa: F401
            engine = "fastparquet"
        except Exception:
            engine = None

    for (source, date), part in features.groupby(["dataset_source", "event_date"]):
        pdir = out_dir / f"dataset_source={source}" / f"event_date={date}"
        pdir.mkdir(parents=True, exist_ok=True)
        if engine:
            fpath = pdir / "features.parquet"
            part.to_parquet(fpath, index=False, engine=engine)
            manifest["format"] = "parquet"
        else:
            fpath = pdir / "features.csv"
            part.to_csv(fpath, index=False)
            manifest["format"] = "csv_fallback_parquet_recommended"
        manifest["partitions"].append({"dataset_source": str(source), "event_date": str(date), "path": str(fpath.relative_to(out_dir)), "rows": int(len(part))})
    (out_dir / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def read_offline_store(out_dir: str | Path) -> pd.DataFrame:
    out_dir = Path(out_dir)
    manifest = json.loads((out_dir / "_manifest.json").read_text())
    frames = []
    for part in manifest["partitions"]:
        p = out_dir / part["path"]
        if p.suffix == ".parquet":
            frames.append(pd.read_parquet(p))
        else:
            frames.append(pd.read_csv(p, parse_dates=["event_time"]))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
