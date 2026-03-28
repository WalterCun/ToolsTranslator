from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


# Pattern for valid language codes: "es", "en", "pt_BR", "zh_Hans", "zh_Hans_CN"
_LANG_CODE_RE = re.compile(r"^[a-z]{2}(_[A-Za-z]{2,4})?(_[A-Za-z]{2,4})?$")


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
        """Detect language code from filename.

        Examples:
            es.json -> es
            messages.es.json -> es
            pt_BR.json -> pt_BR
            zh_Hans.yaml -> zh_Hans

        Returns None if no valid language code is detected.
        """
        # Check dotted names first: "messages.es" -> extract "es"
        if "." in self.stem:
            candidate = self.stem.split(".")[-1]
            if _LANG_CODE_RE.match(candidate):
                return candidate
            return None

        # Direct name: "es.json" or "pt_BR.json"
        if _LANG_CODE_RE.match(self.stem):
            return self.stem
        return None
