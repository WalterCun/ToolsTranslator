from __future__ import annotations

from pathlib import Path
from typing import Any

from translator.handlers.json_handler import JsonHandler
from translator.handlers.yaml_handler import YamlHandler


def read_mapping(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        return JsonHandler.read(path)
    if path.suffix.lower() in {".yaml", ".yml"}:
        return YamlHandler.read(path)
    raise ValueError(f"Unsupported file format: {path.suffix}")


def write_mapping(path: Path, data: dict[str, Any]) -> None:
    if path.suffix.lower() == ".json":
        JsonHandler.write(path, data)
        return
    if path.suffix.lower() in {".yaml", ".yml"}:
        YamlHandler.write(path, data)
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
