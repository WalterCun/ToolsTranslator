# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/__main__.py """

import logging

from config import settings
from main import main

logging.basicConfig(
    level=logging.INFO,  # Establece el nivel mínimo de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="[%(asctime)s] - [%(name)s] - [%(levelname)s] -> %(message)s",  # Formato del log
    handlers=[
        logging.StreamHandler(),  # Enviar mensajes al terminal
        logging.FileHandler(settings.BASE_DIR / "logs/translate-tools.log", mode="a") if settings.DEBUG else ...
    ]
)

log = logging.getLogger(__name__)

if __name__ == "__main__":
    import sys

    # sys.argv = [
    #     "translator",
    #     "auto-translate", "D:\Coders\ToolsTranslator\struct_files\en.json",
    #     "--lang", "es"
    # ]
    # main()

    # sys.argv = [
    #     "translator",
    #     "auto-translate", "D:\Coders\ToolsTranslator\struct_files\en.json",
    #     "--lang", "es",
    #     '--output', 'D:\Coders\ToolsTranslator\struct_files\output',
    # ]
    # main()

    sys.argv = [
        "translator",
        "auto-translate", "D:\Coders\ToolsTranslator\struct_files\en.json",
        "--lang", "es", "en", "fr",
        '--output', 'D:\Coders\ToolsTranslator\struct_files\output',
    ]
    main()

    # sys.argv = [
    #     "cli.py", "auto_translate", "D:\Coders\ToolsTranslator\struct_files\en.json",
    #     "--lang", "all",
    #     "--output", "D:\Coders\ToolsTranslator\struct_files\output",
    #     "--overwrite"
    # ]
    # main()
    #
    # sys.argv = ["cli.py", "auto_translate", "D:\Coders\ToolsTranslator\struct_files\en.yml", "--lang", "br"]
    # main()
