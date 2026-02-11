from __future__ import annotations

from urllib.error import HTTPError, URLError

from toolstranslator.adapters.http_client import HttpClient
from toolstranslator.exceptions import ServiceUnavailableError


class LibreTranslateClient:
    """HTTP adapter for LibreTranslate API."""

    def __init__(self, base_url: str, timeout: float = 10.0, client: HttpClient | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client or HttpClient(timeout=timeout)

    def translate(self, text: str, source: str, target: str) -> str:
        payload = {"q": text, "source": source, "target": target, "format": "text"}
        try:
            response = self.client.post(f"{self.base_url}/translate", json_body=payload)
            response.raise_for_status()
            return response.json()["translatedText"]
        except (HTTPError, URLError, KeyError, ValueError) as exc:
            raise ServiceUnavailableError(
                "LibreTranslate unavailable or returned invalid response."
            ) from exc

    async def translate_async(self, text: str, source: str, target: str) -> str:
        payload = {"q": text, "source": source, "target": target, "format": "text"}
        try:
            response = await self.client.post_async(f"{self.base_url}/translate", json_body=payload)
            response.raise_for_status()
            return response.json()["translatedText"]
        except (HTTPError, URLError, KeyError, ValueError) as exc:
            raise ServiceUnavailableError(
                "LibreTranslate unavailable or returned invalid response."
            ) from exc
