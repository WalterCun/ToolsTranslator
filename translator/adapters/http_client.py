from __future__ import annotations

import asyncio
import json
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
    """Thin sync/async HTTP wrapper with stdlib only."""

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def _request(self, method: str, url: str, json_body: dict[str, Any] | None = None) -> SimpleHttpResponse:
        data = None
        headers = {}
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                content = response.read().decode("utf-8")
                payload = json.loads(content) if content else {}
                status_code = getattr(response, "status", 200)
                return SimpleHttpResponse(status_code=status_code, payload=payload)
        except HTTPError:
            raise
        except URLError:
            raise

    def get(self, url: str) -> SimpleHttpResponse:
        return self._request("GET", url)

    def post(self, url: str, json_body: dict[str, Any]) -> SimpleHttpResponse:
        return self._request("POST", url, json_body)

    async def get_async(self, url: str) -> SimpleHttpResponse:
        return await asyncio.to_thread(self.get, url)

    async def post_async(self, url: str, json_body: dict[str, Any]) -> SimpleHttpResponse:
        return await asyncio.to_thread(self.post, url, json_body)
