from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from translator.exceptions import TranslationFileError

log = logging.getLogger("translator")


class JsonHandler:
    """JSON read/write utility with atomic write semantics."""

    @staticmethod
    def read(path: Path) -> dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as exc:
            log.error("Corrupt JSON file: %s — %s", path, exc)
            raise TranslationFileError(
                f"Invalid JSON in {path}: {exc.msg} (line {exc.lineno}, col {exc.colno})"
            ) from exc
        except OSError as exc:
            raise TranslationFileError(f"Cannot read {path}: {exc}") from exc

    @staticmethod
    def write(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Create temp file in the same directory to ensure atomic move works across filesystems
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        
        try:
            tmp_path.replace(path)
        except OSError:
            os.remove(tmp_path)
            raise
