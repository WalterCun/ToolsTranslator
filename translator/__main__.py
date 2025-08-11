# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/__main__.py """

import logging

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
    '''
    EXAMPLES:
    
    - python -m translator auto-translate D:\Coders\ToolsTranslator\struct_files\en.json --lang es
    
    - python -m translator auto-translate D:\Coders\ToolsTranslator\struct_files\en.json --lang es --output D:\Coders\ToolsTranslator\struct_files\output
    
    - python -m translator auto-translate D:\Coders\ToolsTranslator\struct_files\en.json --output D:\Coders\ToolsTranslator\struct_files\output --lang en
    
    - python -m translator auto-translate D:\Coders\ToolsTranslator\struct_files\en.yml --lang br --output D:\Coders\ToolsTranslator\struct_files\output
    
    - python -m translator auto-translate D:\Coders\ToolsTranslator\struct_files\en.json --lang all --output D:\Coders\ToolsTranslator\struct_files\output --overwrite
    
    - python -m translator auto-translate D:\Coders\ToolsTranslator\struct_files\en.json --lang all --output D:\Coders\ToolsTranslator\struct_files\output --overwrite --force
    
    - python -m translator auto-translate D:\Coders\ToolsTranslator\struct_files\en.json --lang all --output D:\Coders\ToolsTranslator\struct_files\output --overwrite --force --force-all
    
    - python -m translator add D:\Coders\ToolsTranslator\struct_files\ch.json "hola mundo" --lang es
    '''

    main()
