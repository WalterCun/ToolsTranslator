# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/tools/config_logging.py """

import logging


def config_logging(logger: logging.Logger,
                   level: int = logging.INFO,
                   formatter_logging: str = '[%(asctime)s] - [%(levelname)s] -> %(message)s'
                   ):
    logger.setLevel(level)

    # Crear un handler que imprime en la consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)  # Cambiar a DEBUG si necesitas más detalle
    # Crear formato para los mensajes de log
    formatter = logging.Formatter(formatter_logging)
    console_handler.setFormatter(formatter)

    # Añadir el handler al logger principal
    logger.addHandler(console_handler)
