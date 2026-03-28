"""Translation adapters — pluggable backends for translation services."""

from translator.adapters.base import TranslationAdapter
from translator.adapters.cached import CachedAdapter
from translator.adapters.fallback import FallbackAdapter
from translator.adapters.libretranslate import LibreTranslateClient

__all__ = ["TranslationAdapter", "LibreTranslateClient", "FallbackAdapter", "CachedAdapter"]
