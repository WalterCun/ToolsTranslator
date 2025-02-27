import os
import argparse
import logging
import re
from pathlib import Path
from core import Translator

logger = logging.getLogger(__name__)

# Expresión regular para detectar el idioma en el nombre del archivo
LANG_PATTERN = re.compile(r"\b([a-z]{2}(-[a-z]{2})?)\b", re.IGNORECASE)

def extract_lang_from_filename(filename: str) -> str:
    """ Extrae el idioma desde el nombre del archivo si es válido. """
    match = LANG_PATTERN.search(filename)
    return match.group(1) if match else None

def main():
    parser = argparse.ArgumentParser(description="Herramienta CLI para manejar traducciones")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando para agregar texto
    add_parser = subparsers.add_parser("add", help="Agregar una nueva traducción")
    add_parser.add_argument("file", type=Path, help="Archivo JSON donde se almacenará la traducción")
    add_parser.add_argument("value", help="El texto traducido")
    add_parser.add_argument("--key", required=True, help="La clave de la traducción")
    add_parser.add_argument("--lang", help="El idioma (e.g., es, en, fr)", default="es")

    # Subcomando para traducción automática
    auto_translate_parser = subparsers.add_parser("auto_translate", help="Auto translate")
    auto_translate_parser.add_argument("file", type=Path, help="Archivo JSON a traducir")
    auto_translate_parser.add_argument("--base", help="Idioma base (obligatorio si no está en el nombre del archivo)")
    auto_translate_parser.add_argument("--langs", required=True, nargs="*", help="Idiomas destino (e.g., es, en, fr)")
    auto_translate_parser.add_argument("--force", action="store_true", help="Forzar traducciones")

    args = parser.parse_args()

    if args.command == "add":
        handle_add_text(args)
    elif args.command == "auto_translate":
        handle_auto_translate(args)

def handle_add_text(args):
    """ Maneja el comando 'add' para agregar traducciones. """
    file_path = args.file

    if not file_path.parent.exists():
        print(f"Error: El directorio '{file_path.parent}' no existe.")
        return

    print(f"Las nuevas traducciones se guardarán en: {file_path.parent}")

    translator = Translator(file_path.parent)
    translator.add_trans(key=args.key, lang=args.lang, value=args.value)
    print(f"Traducción agregada en {file_path}: {args.key} -> {args.value} en {args.lang}.")

def handle_auto_translate(args):
    """ Maneja la traducción automática desde un archivo JSON. """
    file_path = args.file

    if not file_path.exists():
        print(f"Error: El archivo '{file_path}' no existe.")
        return

    # Obtener el directorio donde está el archivo
    file_dir = file_path.parent

    # Detectar el idioma base desde el nombre del archivo o usar --base
    detected_lang = extract_lang_from_filename(file_path.name)
    base_lang = args.base if args.base else detected_lang

    if not base_lang:
        print("Error: No se detectó el idioma base en el nombre del archivo. Usa --base para especificarlo.")
        return

    print(f"Idioma base detectado: {base_lang}")
    print(f"Las nuevas traducciones se guardarán en: {file_dir}")

    # Pasar el directorio como objeto Path a Translator
    translator = Translator(file_dir)
    translator.auto_translate(base=base_lang, langs='all' if 'all' in args.langs else args.langs, force=args.force)
    print(f"Traducciones desde '{base_lang}' auto traducidas en '{file_dir}'.")

if __name__ == "__main__":
    import sys
    sys.argv = ["cli.py", "auto_translate", "struct_files/en.json", "--lang", "es"]
    main()
