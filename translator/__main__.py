# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/__main__.py """

import logging
import sys

from translator.main import main

logging.basicConfig(
    level=logging.WARN,  # Establece el nivel mínimo de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="[%(asctime)s] - [%(name)s] - [%(levelname)s] -> %(message)s",  # Formato del log
    handlers=[
        logging.StreamHandler(),  # Enviar mensajes al terminal
    ]
)

log = logging.getLogger(__name__)

if __name__ == "__main__":
#     import sys
#
    sys.argv = [
        "translator",
        "auto-translate", r"D:\Coders\ToolsTranslator\struct_files\en.json",
        "--lang", "es"
    ]


    # sys.argv = [
    #     "translator",
    #     "auto-translate", "D:\Coders\ToolsTranslator\struct_files\en.json",
    #     "--lang", "es",
    #     '--output', 'D:\Coders\ToolsTranslator\struct_files\output',
    # ]


    # sys.argv = [
    #     "translator",
    #     "auto-translate", "D:\Coders\hhg-website\src\i18n\jes.json",
    #     "--output", "D:\Coders\harmonyhotel_web\src\i18n",
    #     "--lang", "en"
    # ]


    # sys.argv = [
    #     "cli.py", "auto_translate", "D:\Coders\ToolsTranslator\struct_files\en.json",
    #     "--lang", "all",
    #     "--output", "D:\Coders\ToolsTranslator\struct_files\output",
    #     "--overwrite"
    # ]

    #
    # sys.argv = ["cli.py", "auto_translate", "D:\Coders\ToolsTranslator\struct_files\en.yml", "--lang", "br"]
    main()
