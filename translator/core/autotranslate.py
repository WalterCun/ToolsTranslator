#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/core/autotranslate.py """

import logging
from argparse import Namespace
from pathlib import Path
from typing import List, Tuple

from parses.yaml import YAML
from tools.config_logging import config_logging
from parses import JSON
from api.translate_api import LibreTranslate
from models.info_file import InfoFile

log = logging.getLogger(__name__)
config_logging(log, logging.WARNING)


class AutoTranslate:
    """
    Represents a class for automated translation tasks leveraging the LibreTranslate API.
    This class provides functionality for organizing translation metadata, managing file
    paths, handling supported languages, and processing translation operations based on
    various input conditions.

    It primarily focuses on translating JSON-based content and supports additional formats
    like YAML and TS with a flexible mechanism to specify translation settings.

    :ivar api: Provides access to the LibreTranslate API methods and functions.
    :type api: LibreTranslate
    :ivar language_support: List of languages supported by the LibreTranslate API for the
        given metadata or argument configuration.
    :type language_support: List[str]
    :ivar path: The primary path of the file to be translated.
    :type path: str
    :ivar translations_dir: Directory path where translations will be stored or fetched.
    :type translations_dir: Path
    :ivar lang_work: Specifies the default working language or "all" to target multiple
        languages.
    :type lang_work: str or List[str]
    :ivar name: The name attribute derived from the metadata pertaining to the input file.
    :type name: str
    :ivar ext: The extension of the specific translation file format to be processed.
    :type ext: str
    :ivar args: Parsed Namespace object from argparse, providing CLI input options.
    :type args: Namespace
    :ivar force: Boolean flag to determine if translation operations overwrite constraints
        by force.
    :type force: bool
    :ivar overwrite: Boolean flag to enable overwriting previously existing translation
        data or files.
    :type overwrite: bool
    """

    def __init__(self, meta: InfoFile, force=False, overwrite=False, args: Namespace = None):
        """
        Initializes an instance of this class, responsible for setting up API usage,
        file paths, translation directories, and managing input parameters. This class
        is tailored to handle translation operations using the LibreTranslate API, and
        it organizes the environment based on the metadata provided.

        :param meta: Metadata for the translation. Contains relevant information about
            the file, its path, directory structure, and language details.
        :type meta: InfoFile
        :param force: Flag that indicates whether the operation should forcibly
            overwrite certain conditions during processing. Defaults to False.
        :type force: bool
        :param overwrite: Flag that indicates if existing data should be overwritten.
            Defaults to False.
        :type overwrite: bool
        """
        self.api = LibreTranslate()
        self.language_support = self.api.get_supported_languages(args.base or meta.lang or 'all', True)

        self.path = meta.path
        self.translations_dir = Path(meta.directory)
        if self.translations_dir.exists():
            self.translations_dir.mkdir(parents=True, exist_ok=True)
        self.lang_work = meta.lang or 'all'
        self.name = meta.name
        self.ext = meta.ext

        self.args = args

        self.force = force
        self.overwrite = overwrite

    def extract_parse_file(self, path=None, to_dict: bool = False) -> list[tuple[str, str]] or dict or None:

        file_path = Path(path) if path else Path(self.path)
        if not file_path.exists():
            return {} if to_dict else []

        if self.ext.lower() == 'json':
            json_instance = JSON(str(file_path))
            data = json_instance.get_content_json_file()
            serialized = json_instance.serializer_json(data)
            return {k: v for k, v in serialized} if to_dict else serialized
        elif self.ext.lower() in ('yaml', 'yml'):
            yml_instance = YAML(str(file_path))
            data = yml_instance.get_content_yaml_file()
            return yml_instance.serializer_yaml(data)
        elif self.ext.lower() == 'ts':
            log.warning("Formato 'ts' aún no implementado.")
            return None
        else:
            raise ValueError(f"Formato no soportado {self.ext}")

    def json_worker(self, lang_work: list or str, lang_file: str, output_dir: str or Path, force: bool,
                    overwrite: bool):

        base_data = self.extract_parse_file(to_dict=True)
        if not isinstance(lang_work, list):
            lang_work = [lang_work]

        path_output = Path(output_dir) if output_dir else self.translations_dir
        path_output.mkdir(parents=True, exist_ok=True)

        for lang in lang_work:
            log.info(f'Traduciendo al idioma: {lang}')
            translated: List[Tuple[str, str]] = []
            output_file = path_output / f"{lang}.json"

            # Se intenta leer el archivo traducido previamente, si existe
            try:
                new_data = self.extract_parse_file(output_file, to_dict=True)
            except Exception as e:
                log.info(f"No se pudo leer {output_file}, se creará uno nuevo. Error: {e}")
                new_data = {}

            for key, base_value in base_data.items():
                out_value = new_data.get(key)
                # Si no hay traducción previa o se indica forzar/overwrite, se traduce
                if out_value is None or overwrite or force:
                    log.debug(f"Traduciendo la clave: {key} (traducción previa: {out_value})")
                    try:
                        translated_text = self.api.translate(base_value, lang_file, lang)
                    except Exception as e:
                        log.error(f"Error al traducir {key}: {e}")
                        translated_text = None
                    log.info(f'{key} ({lang_file} -> {lang}): {translated_text}')
                    translated.append((key, translated_text))
                else:
                    log.info(f'Usando traducción existente para {key}: {out_value}')
                    translated.append((key, out_value))

            json_instance = JSON(str(output_file))
            try:
                # Se guarda el resultado en el archivo de salida
                json_instance.save_json_file(json_instance.deserializar_json(translated))
            except Exception as e:
                log.error(f"Error al guardar {output_file}: {e}")

            log.info('Finish convert languages packages......')

    def worker(self, base: str = None, langs: list or str = None):
        """
        Executes work-related tasks based on the provided parameters. This method performs
        actions specified for the given input languages and modifies the behavior based
        on the provided arguments, ensuring proper handling of work cases with optional
        overwriting or forced conditions. Throws an assertion error if no language is
        specified.

        :param base: Base path or configuration to be used during operations. Defaults to None.
        :type base: str, optional
        :param langs: Specifies the languages as a list or string for which the operations
                      will apply. Must not be None or empty.
        :type langs: list or str, optional
        :param force: If True, forces the operations to proceed, potentially bypassing
                      standard constraints. Defaults to False.
        :type force: bool, optional
        :param overwrite: If True, allows overwriting of existing data or configurations
                          during the operation. Defaults to False.
        :type overwrite: bool, optional
        :return: The result of the worker operation or None if the process terminates early.
        :rtype: Any
        """

        if base:
            lang_file = base
        elif self.args and getattr(self.args, 'base', None):
            lang_file = self.args.base
        elif self.name in self.language_support:
            lang_file = self.name
        else:
            lang_file = self.lang_work

        # Determinar los idiomas de trabajo (lang_work)
        if langs:
            if isinstance(langs, list):
                lang_work = [lang for lang in langs if lang in self.language_support]
            elif isinstance(langs, str):
                lang_work = [langs] if langs in self.language_support else []
            else:
                lang_work = []
        elif self.args and getattr(self.args, 'langs', None):
            if isinstance(self.args.langs, list) and 'all' in self.args.langs:
                lang_work = [lang for lang in self.language_support if lang != lang_file]
            elif isinstance(self.args.langs, list):
                lang_work = [x for x in self.args.langs if x in self.language_support]
            else:
                lang_work = []
        else:
            lang_work = [self.lang_work] if isinstance(self.lang_work, str) else self.lang_work

        if not lang_work:
            log.error("No se especificaron idiomas válidos para trabajar.")
            return None

        if self.ext.lower() == 'json':
            output_dir = self.args.output if self.args and getattr(self.args, 'output', None) else self.translations_dir
            self.json_worker(lang_work, lang_file, output_dir, self.force, self.overwrite)
        else:
            log.error(f"Formato no soportado {self.ext}. Notificar al administrador (waltercunbustamante@gmail.com)")
