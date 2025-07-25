# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/__init__.py """

__version__ = "0.1.5"

from .core.translate import Translator
from .config import settings
from .api.translate_api import LibreTranslate

# Importación condicional de AutoTranslate
try:
    from .core.autotranslate import AutoTranslate
    __all__ = ['AutoTranslate', 'Translator', 'settings', 'LibreTranslate']
except ImportError:
    # AutoTranslate no está disponible, probablemente faltan dependencias YAML
    __all__ = ['Translator', 'settings', 'LibreTranslate']
