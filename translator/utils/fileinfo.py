from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class TranslateFile:
    path: Path

    @property
    def directory(self) -> Path:
        return self.path.parent

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def stem(self) -> str:
        return self.path.stem

    def detect_lang_from_name(self) -> str | None:
        # es.json -> es, messages.es -> es
        if "." in self.stem:
            return self.stem.split(".")[-1]
        if len(self.stem) in (2, 5):
            return self.stem
        return None
