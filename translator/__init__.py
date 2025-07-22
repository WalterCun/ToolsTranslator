# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/__init__.py """

__version__ = "0.1.5"

from .core.autotranslate import AutoTranslate
from .core.translate import Translator
from .config import settings
from .api.translate_api import LibreTranslate

__all__ = ['AutoTranslate', 'Translator','settings','LibreTranslate']