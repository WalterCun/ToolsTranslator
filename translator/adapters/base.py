"""Translation adapter protocol — the contract for any translation backend."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class TranslationAdapter(Protocol):
    """Protocol that any translation backend must implement.

    Example implementations:
        - LibreTranslateClient (included)
        - Custom adapter wrapping Google Translate, DeepL, OpenAI, etc.

    Usage:
        class MyAdapter:
            def available(self) -> tuple[bool, str]:
                return True, "ok"

            def translate(self, text: str, source: str, target: str) -> str:
                return f"[{target}] {text}"

        trans = Translator(lang="es", adapter=MyAdapter())
    """

    def available(self) -> tuple[bool, str]:
        """Check if the translation service is reachable.

        Returns:
            Tuple of (is_available, reason).
        """
        ...

    def translate(self, text: str, source: str, target: str) -> str:
        """Translate text from source language to target language.

        Args:
            text: The text to translate.
            source: Source language code (e.g., "es", "en", "auto").
            target: Target language code (e.g., "fr", "de").

        Returns:
            The translated text.
        """
        ...
