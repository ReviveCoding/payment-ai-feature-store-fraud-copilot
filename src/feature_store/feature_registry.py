from __future__ import annotations
from pathlib import Path
import yaml


def load_feature_registry(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def flatten_feature_names(registry: dict) -> list[str]:
    out = []
    for group in registry.get("feature_groups", {}).values():
        out.extend(group.get("features", []))
    return sorted(set(out))
