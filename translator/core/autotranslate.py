#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" translator/core/autotranslate.py """

import logging
from argparse import Namespace
from pathlib import Path
from typing import Optional, Union, Dict, List

import importlib.util
from translator.parses.tjson import JSON

from translator.utils import TranslateFile
from translator.utils.extract_info_file import extract_first_primitive_value

# logging.basicConfig(
#     level=logging.WARN,  # Establece el nivel mínimo de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#     format="[%(asctime)s] - [%(name)s] - [%(levelname)s] -> %(message)s",  # Formato del log
#     handlers=[
#         logging.StreamHandler(),  # Enviar mensajes al terminal
#     ]
# )

log = logging.getLogger(__name__)

# Check if the YAML package is available
try:
    if importlib.util.find_spec('yaml'):
        from translator.parses.tyaml import YAML
except ImportError:
    YAML = None
    log.warning("YAML package is not available. Please install 'pyyaml' package to process YAML files.")


class AutoTranslate:
    """
    Automatiza la traducción de archivos con detección de idioma y soporte de API.

    Esta clase facilita traducir contenidos a múltiples idiomas, detectando el idioma base
    del archivo y utilizando una API (LibreTranslate) para generar las traducciones.
    Además, permite serializar/deserializar archivos (JSON/YAML) y guardar los resultados
    en formato anidado o plano según preferencia.

    Atributos principales:
    - api: Instancia de la API de traducción (LibreTranslate).
    - language_support: Lista de idiomas soportados por la API.
    - fileTranslation: Metadatos y contenido del archivo a traducir (TranslateFile).
    - lang_work: Idioma(s) detectado(s) o seleccionado(s) para trabajar.
    - confidence: Confianza de la detección del idioma.
    - args: Parámetros de configuración (Namespace) provenientes de la CLI u otros.

    Ejemplo de uso:
        >>> from argparse import Namespace
        >>> from pathlib import Path
        >>> from translator.utils import TranslateFile
        >>> from translator.core.autotranslate import AutoTranslate
        >>> tf = TranslateFile(Path('langs/es.json'))
        >>> args = Namespace(base='es', langs=['en', 'fr'], output=tf.directory, force=False, overwrite=False, nested=True)
        >>> AutoTranslate(tf, args=args).worker()
    """

    def __init__(self, file_translation: TranslateFile, args: Namespace = Namespace(base=None)):
        """
        Inicializa el traductor automático con detección de idioma y configuración de API.

        :param file_translation: Instancia de TranslateFile con la ruta, metadatos y contenido del archivo base.
        :type file_translation: TranslateFile
        :param args: Opciones de configuración (Namespace), por ejemplo base, langs, output, force, overwrite, nested.
        :type args: Namespace

        Ejemplo:
            >>> from argparse import Namespace
            >>> from translator.utils import TranslateFile
            >>> tf = TranslateFile('langs/es.json')
            >>> args = Namespace(base='es', langs=['en'], output=tf.directory, force=False, overwrite=False, nested=True)
            >>> at = AutoTranslate(tf, args)
        """
        from translator.api.translate_api import LibreTranslate
        self.api = LibreTranslate()
        self.language_support = self.api.get_supported_languages(args.base or 'all', True)

        self.fileTranslation = file_translation

        # self.path = str(meta.path)

        # self.translations_dir = Path(meta.directory)
        # self.fileTranslation.directory.mkdir(parents=True, exist_ok=True)
        self.lang_work, self.confidence = self.api.detect_language(
            extract_first_primitive_value(self.fileTranslation.content)) or (
                                              'all', -1.0)
        # self.name = meta.name
        # self.ext = meta.ext

        self.args = args

    def _get_target_languages(self, langs, lang_file):
        """
        Determina la lista de idiomas destino válidos.

        - Si se pasa una lista o cadena, filtra contra los idiomas soportados.
        - Si se usan argumentos de CLI (args.langs), respeta 'all', overwrite y exclusiones del idioma base.
        - Si no hay argumentos, usa el idioma detectado.

        :param langs: Lista o cadena con los idiomas destino.
        :param lang_file: Idioma base (usado para excluir cuando no se sobrescribe).
        :return: Lista de códigos de idioma válidos.
        """
        if langs:
            if isinstance(langs, list):
                return [lang for lang in langs if lang in self.language_support]
            if isinstance(langs, str) and langs in self.language_support:
                return [langs]
            return []

        if self.args and hasattr(self.args, 'langs'):
            langs_from_args = self.args.langs
            if isinstance(langs_from_args, list):
                if 'all' in langs_from_args:
                    return [lang for lang in
                            self.language_support] if self.args.overwrite else [lang for lang in self.language_support
                                                                                if
                                                                                lang != lang_file]
                return [lang for lang in langs_from_args if
                        lang in self.language_support] if self.args.overwrite else [lang for lang in langs_from_args if
                                                                                    lang in self.language_support if
                                                                                    lang != lang_file]

        if isinstance(self.lang_work, str):
            return [self.lang_work]

        return self.lang_work

    def _process_language_translation(self, lang: str, lang_file: str, base_data: dict, output_file: Path, force: bool,
                                      overwrite: bool) -> Union[list[tuple[str, str]]]:
        """
        Procesa la traducción para un idioma específico, reutilizando traducciones existentes si están disponibles.

        :param lang: Idioma objetivo.
        :param lang_file: Idioma base del archivo de origen.
        :param base_data: Datos base (clave -> texto) del idioma origen.
        :param output_file: Ruta del archivo de salida para este idioma.
        :param force: Si es True, fuerza traducir aunque exista traducción previa.
        :param overwrite: Si es True, sobrescribe traducciones existentes.
        :return: Diccionario con los datos traducidos.
        """
        try:
            translated_data = self.extract_parse_file(output_file, to_dict=True)
        except Exception as e:
            log.info(f"No se pudo leer el archivo {output_file}, se procede a crear uno nuevo. Error: {e}")
            translated_data = {}

        for key, base_value in base_data.items():
            existing_value = translated_data.get(key)
            if existing_value is None or force or overwrite:
                translation = self._translate_key(base_value, lang_file, lang, key)
                translated_data[key] = translation
            else:
                log.info(f'Usando traducción existente para {key}: {existing_value}')

        return translated_data

    def _translate_key(self, base_value: str, lang_file: str, lang: str, key: str) -> Optional[str]:
        """
        Traduce el valor de una clave.
        
        :param base_value: Texto base a traducir.
        :param lang_file: Idioma origen del archivo base.
        :param lang: Idioma destino.
        :param key: Clave asociada al texto.
        :return: Texto traducido o None si la traducción falla.
        """
        try:
            translated_text = self.api.translate(base_value, lang_file, lang)
            log.info(f'{key} ({lang_file} -> {lang}): {translated_text}')
            return translated_text
        except Exception as e:
            log.error(f"Error al traducir {key}: {e}")
            return None

    @staticmethod
    def _save_translated_data(output_file: Path, translated_data: Optional[List[tuple[str, str]] or Dict[str, str]],
                              nested: bool = True):
        """
        Guarda datos traducidos en un archivo JSON, ya sea como estructura anidada
        (nested=True) o como diccionario plano con claves separadas por puntos (nested=False).

        :param output_file: Ruta del archivo de salida.
        :param translated_data: Lista de tuplas (clave, valor) o diccionario clave->valor.
        :param nested: Si True, guarda anidado; si False, guarda plano.
        :return: None
        """
        json_instance = JSON(str(output_file))
        try:
            if nested:
                # Asegurar iterable de (clave, valor)
                items = translated_data.items() if isinstance(translated_data, dict) else translated_data
                json_instance.save_json_file(json_instance.deserializar_json(items))
            else:
                # Guardar como diccionario plano
                flat_dict = translated_data if isinstance(translated_data, dict) else dict(translated_data or [])
                json_instance.save_json_file(flat_dict)
        except Exception as e:
            log.error(f"Error al guardar {output_file}: {e}")

    def extract_parse_file(self, path: Optional[Path] = None, to_dict: bool = False) -> Optional[
        list[tuple[str, str]] or dict or None]:
        """
        Extrae y parsea un archivo según su extensión (JSON/YAML/YML).

        Dependiendo de `to_dict`, devuelve un diccionario (True) o una lista de tuplas
        (False). Si la ruta no existe, retorna un dict vacío (to_dict=True) o una lista vacía.
        Para extensiones no soportadas se lanza ValueError.

        :param path: Ruta del archivo a procesar. Si es None usa la ruta inicial del objeto.
        :param to_dict: Si True, devuelve dict; si False, lista de tuplas.
        :type path: str | Path | None
        :type to_dict: bool
        :return: Contenido serializado del archivo según `to_dict` y formato.
        :rtype: list[tuple[str, str]] | dict | None
        :raises ValueError: Si se usa una extensión no soportada.
        """
        file_path = path if isinstance(path, Path) else path if path else Path(self.fileTranslation.path)
        if not file_path.exists():
            return {} if to_dict else []

        if self.fileTranslation.ext.lower() == 'json':
            json_instance = JSON(str(file_path))
            data = json_instance.get_content_json_file()
            serialized = json_instance.serializer_json(data)
            return {k: v for k, v in serialized} if to_dict else serialized
        elif self.fileTranslation.ext.lower() in ('yaml', 'yml'):
            if YAML is None:
                log.error("YAML package is not available. Please install 'pyyaml' package to process YAML files.")
                return {} if to_dict else []
            yml_instance = YAML(str(file_path))
            data = yml_instance.get_content_yaml_file()
            return yml_instance.serializer_yaml(data)
        elif self.fileTranslation.ext.lower() == 'ts':
            log.warning("Formato 'ts' aún no implementado.")
            return None
        else:
            raise ValueError(f"Formato no soportado {self.fileTranslation.ext}")

    def json_worker(self, lang_work: list or str, lang_file: str, output_dir: Path, force: bool,
                    overwrite: bool):
        """
        Processes and translates JSON language files for a given language (s) and saves the translated
        content to a specified output directory. Language files are handled either from a provided
        file or a list of them. Also ensures that existing translations are used unless
        `force` or `overwrite` options are enabled.

        :param lang_work: A list or single string representing the target language(s) for translation.
        :param lang_file: The path of the language file used as a basis for translation.
        :param output_dir: The directory where the translated JSON files will be stored.
        :param force: A boolean flag to force translation even if a previous translation exists.
        :param overwrite: A boolean flag to overwrite previously translated content.
        :return: None
        """
        base_data = self.extract_parse_file(to_dict=True)

        lang_work = [lang_work] if isinstance(lang_work, str) else lang_work  # Asegurar que sea una lista
        # output_path = Path(output_dir) if output_dir else self.fileTranslation.directory
        output_dir.mkdir(parents=True, exist_ok=True)

        for lang in lang_work:
            log.info(f'Traduciendo al idioma: {lang}')
            output_file = output_dir / f"{lang}.json"
            translated_data = self._process_language_translation(lang, lang_file, base_data, output_file, force,
                                                                 overwrite)
            # Determinar preferencia de anidamiento para la salida
            nested_pref = True
            if hasattr(self.args, 'flat') and getattr(self.args, 'flat', False):
                nested_pref = False
            elif hasattr(self.args, 'nested') and getattr(self.args, 'nested', False):
                nested_pref = True
            self._save_translated_data(output_file, translated_data, nested=nested_pref)

        log.info('Finish converting language packages.')

    def worker(self, base: str = None, langs: list | str = None) -> None:
        """
        Processes language files for translation based on the provided base and language options.

        The function determines the correct language file to work with and identifies the valid
        languages for translation. It uses the class attributes and provided arguments to
        select the necessary configurations. If valid settings are not provided or the file format
        is unsupported, it logs an appropriate error message.

        :param base: Optional base language file to use for translation. If not provided, defaults
                     are determined based on the instance's attributes.
        :type base: Str, optional
        :param langs: A list or a single string specifying the target languages for translation.
                      Only languages supported by the instance will be considered.
        :type langs: List or str, optional
        :return: None is returned if there are no valid languages for translation or if an
                 unsupported file format is provided.
        :rtype: None
        """

        lang_file = (
                base
                or getattr(self.args, 'base', None)
                or self.lang_work
        )

        lang_work = self._get_target_languages(langs, lang_file)

        if not lang_work:
            log.error("No se especificaron idiomas válidos para trabajar.")
            raise ValueError("No se encontro un idioma base para trabajar")

        if self.fileTranslation.ext.lower() == 'json':
            output_dir = Path(getattr(self.args, 'output', None) or self.fileTranslation.directory)
            self.json_worker(
                lang_work=lang_work,
                lang_file=lang_file,
                output_dir=output_dir,
                force=self.args.force,
                overwrite=self.args.overwrite
            )
        elif self.fileTranslation.ext.lower() in ('yaml', 'yml'):
            log.warning("Formato el desarrollo.......")
        else:
            log.error(
                f"Formato no soportado {self.fileTranslation.ext}. Notificar al administrador (waltercunbustamante@gmail.com)")
