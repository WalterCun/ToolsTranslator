from __future__ import annotations

import time
from urllib.error import HTTPError, URLError

from translator.adapters.base import TranslationAdapter  # noqa: F401 — re-export
from translator.adapters.http_client import HttpClient
from translator.exceptions import ServiceUnavailableError, ServerDependencyMissingError


class LibreTranslateClient:
    """HTTP adapter for LibreTranslate API."""

    def __init__(self, base_url: str, timeout: float = 10.0, client: HttpClient | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client or HttpClient(timeout=timeout)
        self._available_cache: tuple[bool, str, float] | None = None
        self._available_ttl = 30.0  # seconds

    def available(self, *, use_cache: bool = True) -> tuple[bool, str]:
        """Checks if the LibreTranslate server is reachable.

        Uses a TTL cache to avoid hitting the server on every translate() call.
        Pass use_cache=False to force a fresh check.
        """
        now = time.time()
        if use_cache and self._available_cache is not None:
            ok, reason, ts = self._available_cache
            if (now - ts) < self._available_ttl:
                return ok, reason

        try:
            response = self.client.get(f"{self.base_url}/languages")
            response.raise_for_status()
            self._available_cache = (True, "ok", now)
            return True, "ok"
        except (HTTPError, URLError, TimeoutError) as exc:
            result = (False, str(exc), now)
            self._available_cache = result
            return False, str(exc)

    def _ensure_available(self) -> None:
        """Raise ServerDependencyMissingError if the server is not reachable."""
        ok, reason = self.available()
        if not ok:
            raise ServerDependencyMissingError(
                "Server translation is unavailable. "
                "Install/start server support and ensure LibreTranslate is reachable. "
                "Hint: pip install toolstranslator[server] && toolstranslator install. "
                f"Details: {reason}"
            )

    def translate(self, text: str, source: str, target: str) -> str:
        self._ensure_available()
        payload = {"q": text, "source": source, "target": target, "format": "text"}
        try:
            response = self.client.post(f"{self.base_url}/translate", json_body=payload)
            response.raise_for_status()
            return response.json()["translatedText"]
        except (HTTPError, URLError, KeyError, ValueError, TimeoutError) as exc:
            raise ServiceUnavailableError(
                "LibreTranslate unavailable or returned invalid response."
            ) from exc

    async def translate_async(self, text: str, source: str, target: str) -> str:
        self._ensure_available()
        payload = {"q": text, "source": source, "target": target, "format": "text"}
        try:
            response = await self.client.post_async(f"{self.base_url}/translate", json_body=payload)
            response.raise_for_status()
            return response.json()["translatedText"]
        except (HTTPError, URLError, KeyError, ValueError, TimeoutError) as exc:
            raise ServiceUnavailableError(
                "LibreTranslate unavailable or returned invalid response."
            ) from exc
