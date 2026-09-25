from pathlib import Path
from typing import Any

import yaml


def load_reference_ranges(path: str | Path) -> list[dict[str, Any]]:
    """Load and validate configured analytes from YAML."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    ranges = raw.get("reference_ranges", [])
    if not isinstance(ranges, list):
        raise ValueError("reference_ranges must be a list")

    required = {"name", "aliases", "unit", "low", "high"}
    for item in ranges:
        if not isinstance(item, dict) or not required.issubset(item):
            raise ValueError("Each reference range needs name, aliases, unit, low, and high")
        if not isinstance(item["aliases"], list) or item["low"] >= item["high"]:
            raise ValueError(f"Invalid reference range for {item.get('name', 'unknown')}")
    return ranges