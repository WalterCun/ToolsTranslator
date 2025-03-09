# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/main.py """

import argparse
import logging
from pathlib import Path

from core import AutoTranslate
from models import InfoFile
from utils import extract_lang_info_from_filename

log = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Herramienta CLI para manejar archivos de traducciones")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando para agregar texto
    add_parser = subparsers.add_parser("add", help="Agregar una nueva traducción")
    add_parser.add_argument("file", type=Path, help="Archivo JSON donde se almacenará la traducción")
    add_parser.add_argument("value", help="El texto traducido")
    add_parser.add_argument("--key", required=True, help="La clave de la traducción")
    add_parser.add_argument("--lang", help="El idioma (e.g., es, en, fr)", default="es")

    # Subcomando para traducción automática
    auto_translate_parser = subparsers.add_parser("auto-translate", help="Auto translate")
    auto_translate_parser.add_argument("file", type=Path, help="Archivo JSON a traducir")
    auto_translate_parser.add_argument("--base", help="Idioma base (obligatorio si no está en el nombre del archivo)")
    auto_translate_parser.add_argument("--output", help="Directorio de salida para los archivos de traduccion")
    auto_translate_parser.add_argument("--langs", required=True, nargs="*", help="Idiomas destino (e.g., es, en, fr)")
    auto_translate_parser.add_argument("--force", action="store_true", help="Forzar traducciones")
    auto_translate_parser.add_argument("--overwrite", action="store_true", help="Sobreescribir traducciones")

    args = parser.parse_args()

    if args.command == "add":
        # handle_add_text(args
        pass
    elif args.command == "auto-translate":
        handle_auto_translate(args)


# def handle_add_text(args):
#     """ Maneja el comando 'add' para agregar traducciones. """
#     file_path = args.file
#
#     if not file_path.parent.exists():
#         log.error(f"El directorio '{file_path.parent}' no existe.")
#         return
#
#     log.info(f"Las nuevas traducciones se guardarán en: {file_path.parent}")
#
#     translator = Translator(file_path.parent)
#     translator.add_trans(key=args.key, lang=args.lang, value=args.value)
#     log.info(f"Traducción agregada en {file_path}: {args.key} -> {args.value} en {args.lang}.")


def handle_auto_translate(args):
    """ Maneja la traducción automática desde un archivo JSON. """

    file_path = args.file
    if not file_path.exists():
        log.error(f"El archivo '{file_path}' no existe.")
        return

    # Detectar el idioma base desde el nombre del archivo o usar --base
    info_file = InfoFile.from_dict(extract_lang_info_from_filename(file_path))

    translator = AutoTranslate(info_file, force=args.force, overwrite=args.overwrite, args=args)
    translator.worker()