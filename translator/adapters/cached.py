"""CachedAdapter — decorator that adds per-key TTL caching to any adapter."""

from __future__ import annotations

import time

from translator.adapters.base import TranslationAdapter


class CachedAdapter:
    """Wraps any TranslationAdapter with per-translation result caching.

    Usage:
        adapter = CachedAdapter(LibreTranslateClient(...), ttl=3600)
        trans = Translator(lang="es", adapter=adapter)
    """

    def __init__(self, adapter: TranslationAdapter, ttl: float = 3600.0) -> None:
        self._adapter = adapter
        self._ttl = ttl
        self._cache: dict[tuple[str, str, str], tuple[str, float]] = {}

    def available(self) -> tuple[bool, str]:
        return self._adapter.available()

    def translate(self, text: str, source: str, target: str) -> str:
        key = (text, source, target)
        now = time.time()
        if key in self._cache:
            result, ts = self._cache[key]
            if (now - ts) < self._ttl:
                return result
        result = self._adapter.translate(text, source, target)
        self._cache[key] = (result, now)
        return result

    def clear_cache(self) -> None:
        """Clear all cached translations."""
        self._cache.clear()

    @property
    def cache_size(self) -> int:
        """Number of cached translations."""
        return len(self._cache)
