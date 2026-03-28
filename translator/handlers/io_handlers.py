from __future__ import annotations

from pathlib import Path
from typing import Any

from translator.exceptions import TranslationFileError
from translator.handlers.json_handler import JsonHandler
from translator.handlers.yaml_handler import YamlHandler


def read_mapping(path: Path) -> dict[str, Any]:
    """Read a JSON or YAML file and return its contents as a dict.

    Raises:
        TranslationFileError: If the file format is unsupported or the file is corrupt.
    """
    if path.suffix.lower() == ".json":
        return JsonHandler.read(path)
    if path.suffix.lower() in {".yaml", ".yml"}:
        return YamlHandler.read(path)
    raise TranslationFileError(f"Unsupported file format: {path.suffix}")


def write_mapping(path: Path, data: dict[str, Any]) -> None:
    """Write a dict to a JSON or YAML file with atomic semantics.

    Raises:
        TranslationFileError: If the file format is unsupported.
    """
    if path.suffix.lower() == ".json":
        JsonHandler.write(path, data)
        return
    if path.suffix.lower() in {".yaml", ".yml"}:
        YamlHandler.write(path, data)
        return
    raise TranslationFileError(f"Unsupported file format: {path.suffix}")


def flatten(data: dict[str, Any], parent: str = "", *, preserve_dynamic: bool = False) -> dict[str, Any]:
    """Flatten nested dict to dotted keys.

    Args:
        data: Nested dictionary to flatten.
        parent: Prefix for dotted keys.
        preserve_dynamic: If True, keep dicts containing "__translate__" as values
                         instead of recursing into them (used by Translator).
    """
    out: dict[str, Any] = {}
    for key, value in data.items():
        full = f"{parent}.{key}" if parent else key
        if isinstance(value, dict):
            if preserve_dynamic and "__translate__" in value:
                out[full] = value
            else:
                out.update(flatten(value, full, preserve_dynamic=preserve_dynamic))
        else:
            out[full] = value
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
