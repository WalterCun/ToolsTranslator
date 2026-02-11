from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from translator.exceptions import ExtraNotInstalledError


class YamlHandler:
    """YAML utility loaded only when `yml` extra is installed."""

    @staticmethod
    def _load_yaml_module() -> Any:
        try:
            import yaml  # type: ignore
        except ImportError as exc:  # pragma: no cover - depends on installation mode
            raise ExtraNotInstalledError(
                "YAML support requires optional dependency. Install: pip install translator[yml]"
            ) from exc
        return yaml

    @classmethod
    def read(cls, path: Path) -> dict[str, Any]:
        yaml = cls._load_yaml_module()
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @classmethod
    def write(cls, path: Path, data: dict[str, Any]) -> None:
        yaml = cls._load_yaml_module()
        path.parent.mkdir(parents=True, exist_ok=True)
        # Create a temp file in the same directory to ensure atomic move works across filesystems
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as tmp:
            yaml.safe_dump(data, tmp, allow_unicode=True, sort_keys=False)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        
        try:
            tmp_path.replace(path)
        except OSError:
            os.remove(tmp_path)
            raise
