"""FallbackAdapter — chains multiple adapters with automatic fallback."""

from __future__ import annotations
import logging
from translator.adapters.base import TranslationAdapter
from translator.exceptions import ServiceUnavailableError

log = logging.getLogger("translator")


class FallbackAdapter:
    """Chains multiple translation adapters. Tries each in order until one succeeds."""

    def __init__(self, *adapters: TranslationAdapter) -> None:
        if not adapters:
            raise ValueError("At least one adapter required")
        self._adapters = adapters

    def available(self) -> tuple[bool, str]:
        for adapter in self._adapters:
            ok, reason = adapter.available()
            if ok:
                return True, f"OK ({adapter.__class__.__name__})"
        return False, "All adapters unavailable"

    def translate(self, text: str, source: str, target: str) -> str:
        last_exc: Exception | None = None
        for adapter in self._adapters:
            try:
                return adapter.translate(text, source, target)
            except Exception as exc:
                last_exc = exc
                log.debug("Adapter %s failed: %s", adapter.__class__.__name__, exc)
                continue
        raise ServiceUnavailableError(f"All {len(self._adapters)} adapters failed") from last_exc
