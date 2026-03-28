"""ToolsTranslator public API."""

__version__ = "1.0.0"

from translator.adapters.base import TranslationAdapter
from translator.adapters.cached import CachedAdapter
from translator.adapters.fallback import FallbackAdapter
from translator.adapters.libretranslate import LibreTranslateClient
from translator.core.translator import Translator

__all__ = [
    "Translator",
    "TranslationAdapter",
    "LibreTranslateClient",
    "FallbackAdapter",
    "CachedAdapter",
]
