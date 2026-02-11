from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from translator.exceptions import ServerDependencyMissingError


def read_mapping(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise ServerDependencyMissingError(
                "YAML requires optional dependency. Install with: pip install toolstranslator[yml]"
            ) from exc
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    raise ValueError(f"Unsupported file format: {path.suffix}")


def write_mapping(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise ServerDependencyMissingError(
                "YAML requires optional dependency. Install with: pip install toolstranslator[yml]"
            ) from exc
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
        return
    raise ValueError(f"Unsupported file format: {path.suffix}")


def flatten(data: dict[str, Any], parent: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in data.items():
        full = f"{parent}.{key}" if parent else key
        if isinstance(value, dict):
            out.update(flatten(value, full))
        else:
            out[full] = str(value)
    return out


def unflatten(data: dict[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for dotted, value in data.items():
        parts = dotted.split(".")
        current = out
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return out
