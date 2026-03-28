from __future__ import annotations

import asyncio
import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class SimpleHttpResponse:
    def __init__(self, status_code: int, payload: dict[str, Any] | list[Any]) -> None:
        self.status_code = status_code
        self.payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HTTPError(url="", code=self.status_code, msg="HTTP error", hdrs=None, fp=None)

    def json(self) -> dict[str, Any] | list[Any]:
        return self.payload


class HttpClient:
    """Thin sync/async HTTP wrapper with stdlib only.

    Supports automatic retry with exponential backoff for transient errors.
    """

    def __init__(self, timeout: float = 10.0, retries: int = 3, base_delay: float = 1.0) -> None:
        self.timeout = timeout
        self.retries = retries
        self.base_delay = base_delay

    def _request(self, method: str, url: str, json_body: dict[str, Any] | None = None) -> SimpleHttpResponse:
        data = None
        headers = {}
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url, data=data, headers=headers, method=method)
        last_exc: Exception | None = None

        for attempt in range(self.retries):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    content = response.read().decode("utf-8")
                    payload = json.loads(content) if content else {}
                    status_code = getattr(response, "status", 200)
                    return SimpleHttpResponse(status_code=status_code, payload=payload)
            except (HTTPError, URLError, TimeoutError) as exc:
                last_exc = exc
                # Don't retry on HTTP 4xx client errors (except 429 Too Many Requests)
                if isinstance(exc, HTTPError) and 400 <= exc.code < 500 and exc.code != 429:
                    raise
                if attempt < self.retries - 1:
                    time.sleep(self.base_delay * (2 ** attempt))

        # All retries exhausted — raise the last exception
        raise last_exc  # type: ignore[misc]

    def get(self, url: str) -> SimpleHttpResponse:
        return self._request("GET", url)

    def post(self, url: str, json_body: dict[str, Any]) -> SimpleHttpResponse:
        return self._request("POST", url, json_body)

    async def get_async(self, url: str) -> SimpleHttpResponse:
        return await asyncio.to_thread(self.get, url)

    async def post_async(self, url: str, json_body: dict[str, Any]) -> SimpleHttpResponse:
        return await asyncio.to_thread(self.post, url, json_body)
