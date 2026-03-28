"""ToolsTranslator public API."""

from translator.adapters.base import TranslationAdapter
from translator.core.translator import Translator

__all__ = ["Translator", "TranslationAdapter"]
