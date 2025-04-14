# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/utils/extract_info_file.py """

import re
from pathlib import Path

from translator import settings
from translator.utils.searches import buscar_path, search_path

LANG_PATTERN = re.compile(r"\b([a-z]{2}(-[a-z]{2})?)\b", re.IGNORECASE)


# def extract_lang_info_from_filename(path: Path) -> dict[str, str or Path]:
#     """
#     Extracts language and other metadata from a file's path.
#
#     This function processes the given file path to decompose it into
#     useful components: the full path as a string, the parent directory,
#     the file extension, the full filename, and an optionally extracted
#     language code if present in the filename.
#
#     :param path: The file path to be analyzed.
#     :type path: Path
#     :return: A dictionary containing the file path, directory, file
#         extension, full filename, and an optional detected language code.
#     :rtype: dict[str, str]
#     """
#     directory = path.parent
#     file, ext = path.name.split(".", 1)
#     match = LANG_PATTERN.search(file)
#
#     return {
#         "path": path,
#         "directory": directory,
#         "lang": str(match.group(1)) if match else None,
#         "ext": ext,
#         "name": path.name
#     }


class TranslateFile:
    _path: Path
    _directory: Path
    _content: str
    _file: str
    _name: str
    _ext: str

    # --------------------------------------------------------------------------------------------------------------

    def __init__(self, path: Path or str):
        if not isinstance(path, Path):
            path = Path(path)

        self.path = path

        self._directory = search_path(settings.BASE_DIR, path)
        self._file, self._ext = path.name.split(".", 1)
        self._extract_content()

    # --------------------------------------------------------------------------------------------------------------

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def directory(self) -> Path:
        return self._directory

    @property
    def file(self) -> str:
        return self._file

    @property
    def name(self) -> str:
        return self._name

    @property
    def ext(self) -> str:
        return self._ext

    @property
    def content(self) -> str:
        return self._content or ""

    # --------------------------------------------------------------------------------------------------------------

    def _extract_content(self):
        try:
            with open(self.directory, "r", encoding="utf-8") as f:
                self._content = f.read()
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
            self._content = ""

    # --------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _is_json(content):
        import json

        try:
            return True, json.loads(content)
        except json.JSONDecodeError:
            return False, None

    @staticmethod
    def _is_i18n(content):
        # Patrón para detectar claves de idioma (ej: "es", 'en') con objetos anidados
        patron = r'''
            (["']{1}([a-z]{2})["']{1})   # Grupo 1: Clave de idioma entre comillas
            \s*:\s*                       # Separador clave-valor
            \{                            # Inicio de objeto
            (?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*  # Contenido del objeto (permite anidados)
            \}                            # Fin de objeto
        '''

        coincidences = re.findall(patron, content, re.VERBOSE | re.MULTILINE)
        return True if len(coincidences) > 0 else None, coincidences

    # --------------------------------------------------------------------------------------------------------------

    def analise_file(self):
        content = self._extract_content()

        validate, data = self._is_json(content)
        if validate:
            # Verifica si todas las claves son códigos de idioma de 2 letras
            if all(re.match(r'^[a-z]{2}$', clave) for clave in data.keys()):
                return "Archivo de idiomas (JSON)"
            else:
                return "JSON genérico"
        validate, data = self._is_i18n(content)
        # Verifica si es archivo de idiomas no-JSON (ej: objeto JS/TS)
        if validate:
            return "Archivo de idiomas (JS/TS)"

        return "Tipo desconocido"


if __name__ == '__main__':
    # path = Path("struct_files/en.json")
    tf = TranslateFile("struct_files/i18n.ts")

    print(tf.directory)
    print(tf.file)
    print(tf.ext)
    print(tf.content)
