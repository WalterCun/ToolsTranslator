from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from translator.exceptions import ServerDependencyMissingError


class TranslationAdapter(Protocol):
    def available(self) -> tuple[bool, str]:
        ...

    def translate(self, text: str, source: str, target: str) -> str:
        ...


@dataclass(slots=True)
class LibreTranslateAdapter:
    base_url: str = "http://localhost:5000"
    timeout_s: float = 5.0

    def available(self) -> tuple[bool, str]:
        url = f"{self.base_url.rstrip('/')}/languages"
        try:
            with urlopen(url, timeout=self.timeout_s) as response:
                if response.status >= 400:
                    return False, f"HTTP {response.status}"
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

        payload = json.dumps({"q": text, "source": source, "target": target, "format": "text"}).encode("utf-8")
        req = Request(
            f"{self.base_url.rstrip('/')}/translate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.timeout_s) as response:
                parsed = json.loads(response.read().decode("utf-8"))
                return str(parsed["translatedText"])
        except (HTTPError, URLError, TimeoutError, KeyError, ValueError) as exc:
            raise ServerDependencyMissingError(f"Remote translation failed: {exc}") from exc
