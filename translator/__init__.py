# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/__init__.py """

from .core.translate import Translator
from .config import settings
from .api.translate_api import LibreTranslate

from .__version import __version__

__author__ = "Walter Cun Bustamante"
__email__ = "waltercunbustamante@gmail.com"


try:
    from .core.autotranslate import AutoTranslate
    __all__ = ['AutoTranslate', 'Translator', 'settings', 'LibreTranslate']
except ImportError:
    # AutoTranslate no está disponible, probablemente faltan dependencias YAML
    __all__ = ['Translator', 'settings', 'LibreTranslate']
