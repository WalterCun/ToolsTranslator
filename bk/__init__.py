#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""bk/__init__.py"""
from bk.__version__ import __version__

__author__ = "Walter Cun Bustamante"
__email__ = "waltercunbustamante@gmail.com"

# Solo exportar la versión durante la construcción
# Los componentes principales se importarán cuando se use el paquete
__all__ = ['__version__']

# Importaciones condicionales - solo si no estamos construyendo
import sys
import os

# Detectar si estamos en proceso de construcción
_is_building = (
        'setup.py' in sys.argv[0] or
        'build' in sys.modules or
        os.environ.get('BUILD_PACKAGE', False)
)

if not _is_building:
    try:
        # Importaciones normales cuando el paquete está instalado
        from bk.core.translate import Translator
        from bk.config import settings
        from bk.api.translate_api import LibreTranslate

        __all__.extend(['Translator', 'settings', 'LibreTranslate'])

        # AutoTranslate opcional
        try:
            from bk.core.autotranslate import AutoTranslate

            __all__.append('AutoTranslate')
        except ImportError:
            pass

    except ImportError:
        # Si hay problemas de importación, continuar solo con __version__
        pass

