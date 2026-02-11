from __future__ import annotations

from typing import Protocol
from urllib.error import HTTPError, URLError

from translator.adapters.http_client import HttpClient
from translator.exceptions import ServiceUnavailableError, ServerDependencyMissingError


class TranslationAdapter(Protocol):
    def available(self) -> tuple[bool, str]:
        ...

    def translate(self, text: str, source: str, target: str) -> str:
        ...


class LibreTranslateClient:
    """HTTP adapter for LibreTranslate API."""

    def __init__(self, base_url: str, timeout: float = 10.0, client: HttpClient | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client or HttpClient(timeout=timeout)

    def available(self) -> tuple[bool, str]:
        """Checks if the LibreTranslate server is reachable."""
        try:
            response = self.client.get(f"{self.base_url}/languages")
            response.raise_for_status()
            return True, "ok"
        except (HTTPError, URLError, TimeoutError) as exc:
            return False, str(exc)

    def translate(self, text: str, source: str, target: str) -> str:
        ok, reason = self.available()
        if not ok:
            raise ServerDependencyMissingError(
                "Server translation is unavailable. "
                "Install/start server support and ensure LibreTranslate is reachable. "
                "Hint: pip install toolstranslator[server] && toolstranslator install. "
                f"Details: {reason}"
            )
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
        ok, reason = self.available()
        if not ok:
            raise ServerDependencyMissingError(
                "Server translation is unavailable. "
                "Install/start server support and ensure LibreTranslate is reachable. "
                "Hint: pip install toolstranslator[server] && toolstranslator install. "
                f"Details: {reason}"
            )
        payload = {"q": text, "source": source, "target": target, "format": "text"}
        try:
            response = await self.client.post_async(f"{self.base_url}/translate", json_body=payload)
            response.raise_for_status()
            return response.json()["translatedText"]
        except (HTTPError, URLError, KeyError, ValueError, TimeoutError) as exc:
            raise ServiceUnavailableError(
                "LibreTranslate unavailable or returned invalid response."
            ) from exc
