from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class SimpleHttpResponse:
    def __init__(self, status_code: int, payload: dict[str, Any]) -> None:
        self.status_code = status_code
        self.payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HTTPError(url="", code=self.status_code, msg="HTTP error", hdrs=None, fp=None)

    def json(self) -> dict[str, Any]:
        return self.payload


class HttpClient:
    """Thin sync/async HTTP wrapper with stdlib only."""

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def post(self, url: str, json_body: dict[str, Any]) -> SimpleHttpResponse:
        data = json.dumps(json_body).encode("utf-8")
        request = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                status_code = getattr(response, "status", 200)
                return SimpleHttpResponse(status_code=status_code, payload=payload)
        except HTTPError:
            raise
        except URLError:
            raise

    async def post_async(self, url: str, json_body: dict[str, Any]) -> SimpleHttpResponse:
        return await asyncio.to_thread(self.post, url, json_body)
