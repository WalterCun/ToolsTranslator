# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/utils/extract_info_file.py """

import re
from pathlib import Path

import logging
from typing import Union

log = logging.getLogger(__name__)


from translator.utils.searches import search_path

# LANG_PATTERN = re.compile(r"\b([a-z]{2}(-[a-z]{2})?)\b", re.IGNORECASE)
PATTERN_I18N = re.compile(
    r"const\s+messages\s*=\s*"  # busca 'const messages ='
    r"(\{[\s\S]*?\})"  # captura desde la primera '{' hasta el '}' más próximo
    r"\s*export\s+default",  # lookahead para asegurar que es el bloque que sigue al export
    re.MULTILINE
)

PATTERN_JSON = r'^[a-z]{2}$'


class TranslateFile:
    _path: Path
    _directory: Path
    _content: dict
    _backup: dict
    _file: str
    _name: str
    _ext: str

    # --------------------------------------------------------------------------------------------------------------

    def __init__(self, path: Union[Path, str]):
        from translator import settings
        if not isinstance(path, Path):
            path = Path(path)

        self.path = search_path(settings.BASE_DIR, path)

        self._directory = self.path.parent
        self._file, self._ext = path.name.split(".", 1)
        self._name = path.stem
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
    def content(self) -> dict:
        return self._content

    # --------------------------------------------------------------------------------------------------------------

    def _extract_content(self) -> None:
        self._content = {}  # Valor predeterminado en caso de error

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read()

            # Intentar parsear como JSON primero
            is_json, json_data = self._is_json(content)
            if is_json:
                self._content = json_data
                return

            # Intentar parsear como archivo i18n si no es JSON
            is_i18n, i18n_data = self._is_i18n(content)
            if is_i18n:
                self._content = i18n_data
                return

            # Si llegamos aquí, no se pudo parsear el contenido
            return

        except FileNotFoundError:
            log.error(f"Error: El archivo {self.path} no existe")
            return
        except PermissionError:
            log.error(f"Error: No hay permisos para leer el archivo {self.path}")
            return
        except Exception as e:
            log.error(f"Error al leer el archivo {self.path}: {e}")
            return

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
        import json
        try:
            coincidences = PATTERN_I18N.search(content)
            data = coincidences.group(1)
            return True if data else None, json.loads(data)
        except json.JSONDecodeError:
            log.error("Error al parsear el contenido del archivo i18n")
        except AttributeError:
            log.error("")
        return False, None

    # --------------------------------------------------------------------------------------------------------------

    # def save(self):
    #     # TODO: Revisar el tema de guardar la informacion modificada
    #     try:
    #         with open(self.path, "w", encoding="utf-8") as f:
    #             f.write(self.content)
    #     except Exception as e:
    #         log.error(f"Error al guardar el archivo: {e}")


if __name__ == '__main__':
    # path = Path("struct_files/en.json")
    tf = TranslateFile("struct_files/i18n.ts")

    # print(tf.path)
    # print(tf.directory)
    # print(tf.file)
    # print(tf.ext)
    print(tf.content)
