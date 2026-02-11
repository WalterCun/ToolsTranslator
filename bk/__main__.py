# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" bk/__main__.py """

import logging

from bk.main import main

logging.basicConfig(
    level=logging.WARN,  # Establece el nivel mínimo de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="[%(asctime)s] - [%(name)s] - [%(levelname)s] -> %(message)s",  # Formato del log
    handlers=[
        logging.StreamHandler(),  # Enviar mensajes al terminal
    ]
)

log = logging.getLogger(__name__)

if __name__ == "__main__":
    r'''
    EXAMPLES:
    # Insertar texto en un archivo JSON con anidacion
    - python -m bk add "texto" --lang es --nested --key main.header.btn.lb
    
    # Insertar texto en un archivo JSON sin anidacion
    - python -m bk add "texto" --lang es --key main.header.btn.lb
    
    # Insertar texto en un archivo JSON con salida en archivo y directorio especifico
    - python -m bk add "texto" --lang es --key main.header.btn.lb --output D:\Coders\ToolsTranslator\struct_files\output


    # Auto traducir un archivo Json con salida en el directorio de origen
    python -m bk auto-translate D:\Coders\ToolsTranslator\langs\es.json --langs en
    
    # Auto traducir un archivo JSON con salida en directorio especifico
    python -m bk auto-translate D:\Coders\ToolsTranslator\langs\es.json --output D:\Coders\ToolsTranslator\langs --langs en
    
    # Auto traducir un archivo JSON con salida en directorio de origen y forzar traducciones
    python -m bk auto-translate D:\Coders\ToolsTranslator\langs\es.json --langs en --force
    
    # Auto traducir un archivo JSON con salida en directorio de origen y sobreescribir traducciones existentes
    python -m bk auto-translate D:\Coders\ToolsTranslator\langs\es.json --langs en --overwrite
    '''

    main()
