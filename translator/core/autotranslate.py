#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" translator/core/autotranslate.py """

import logging
from argparse import Namespace
from pathlib import Path
from typing import List, Tuple, Optional

from translator.parses.tyaml import YAML
# from translator.tools.config_logging import config_logging
from translator.parses.tjson import JSON

# from translator.models.info_file import InfoFile
from translator.utils import TranslateFile

log = logging.getLogger(__name__)


# config_logging(log, logging.WARNING)


class AutoTranslate:
    """
    Manages translation operations, environment setup, and API usage for file translation tasks.

    This class is specifically designed to work with the LibreTranslate API and organize input
    parameters, file paths, and directories for translation. It facilitates the handling of language
    files, providing efficient processing and translation support for different use cases.

    :ivar api: Instance of the LibreTranslate API client, used to perform translations.
    :type api: LibreTranslate
    :ivar language_support: List of languages supported by the LibreTranslate API configuration.
    :type language_support: list[str]
    :ivar path: The file path associated with the metadata information.
    :type path: str
    :ivar translations_dir: Directory where the translated files are stored.
    :type translations_dir: Path
    :ivar lang_work: Language to work with for translations. Defaults to all languages.
    :type lang_work: str
    :ivar name: File name extracted from the metadata, used for processing.
    :type name: str
    :ivar ext: File extension type (e.g., json, yaml, etc.).
    :type ext: str
    :ivar args: Input arguments for translation tasks, including base and language settings.
    :type args: Namespace
    """

    def __init__(self, meta: TranslateFile, args: Namespace = Namespace(base=None)):
        """
        Initializes a new instance of the class, setting up translation API, resolving language and path
        information, and initializing required directories.

        :param meta: Metadata containing file information with attributes such as lang, path, name,
                     ext, and directory.
        :type meta: InfoFile
        :param args: Namespace object containing command-line arguments with optional attributes like base.
        :type args: Namespace
        """
        from translator.api.translate_api import LibreTranslate
        self.api = LibreTranslate()
        self.language_support = self.api.get_supported_languages(args.base or 'all', True)

        self.path = str(meta.path)

        self.translations_dir = Path(meta.directory)
        self.translations_dir.mkdir(parents=True, exist_ok=True)

        self.lang_work = 'all'
        self.name = meta.name
        self.ext = meta.ext

        self.args = args

    def _get_target_languages(self, langs, lang_file):
        """
        Helper method to determine the list of valid target languages.

        :param langs: A list or a single string specifying the target languages.
        :param lang_file: The base language file to exclude from target languages if 'all' is specified.
        :return: A list of valid languages.
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
                    return [lang for lang in self.language_support if lang != lang_file]
                return [lang for lang in langs_from_args if lang in self.language_support]

        if isinstance(self.lang_work, str):
            return [self.lang_work]

        return self.lang_work

    def _process_language_translation(self, lang: str, lang_file: str, base_data: dict, output_file: Path, force: bool,
                                      overwrite: bool) -> dict:
        """
        Processes the translation for a specific language, utilizing existing translations if available.

        :param lang: The language to translate to.
        :param lang_file: The base language file.
        :param base_data: The base language data.
        :param output_file: The path to the output file for this language.
        :param force: Whether to force translation.
        :param overwrite: Whether to overwrite existing translations.
        :return: A dictionary containing the translated data.
        """
        try:
            translated_data = self.extract_parse_file(output_file, to_dict=True)
        except Exception as e:
            log.info(f"No se pudo leer {output_file}, creando uno nuevo. Error: {e}")
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
        Translates a single key value.

        :param base_value: The value to translate.
        :param lang_file: The base language file.
        :param lang: The target language.
        :param key: The key being translated.
        :return: Translated text, or None if translation fails.
        """
        try:
            translated_text = self.api.translate(base_value, lang_file, lang)
            log.info(f'{key} ({lang_file} -> {lang}): {translated_text}')
            return translated_text
        except Exception as e:
            log.error(f"Error al traducir {key}: {e}")
            return None

    def _save_translated_data(self, output_file: Path, translated_data: dict):
        """
        Saves the translated data to the specified output file in JSON format.

        This method takes a file path and a dictionary containing translated data,
        serializes the data to JSON format, and saves it to the given output file.
        If an error occurs during the save process, an error message is logged.

        :param output_file: The file path where the translated data will be saved.
        :param translated_data: A dictionary containing key-value pairs of the
            translated data that needs to be saved.
        :return: None
        """
        json_instance = JSON(str(output_file))
        try:
            json_instance.save_json_file(json_instance.deserializar_json(translated_data.items()))
        except Exception as e:
            log.error(f"Error al guardar {output_file}: {e}")

    def extract_parse_file(self, path: str or Path or None = None, to_dict: bool = False) -> list[tuple[
        str, str]] or dict or None:
        """
        Extracts and parses a file based on the file extension. Supports JSON, YAML, and YML
        formats. Depending on the specified parameters, the method can return either a
        serialized dictionary (when `to_dict` is True) or a list of serialized tuples.

        If the file path does not exist, it will return an empty dictionary for `to_dict=True` or
        an empty list otherwise. For unsupported file extensions, a ValueError is raised.

        :param path: The path of the file to be extracted and parsed. If None, uses the default
                     path provided during initialization (optional).
        :param to_dict: Indicates whether the output should be serialized as a dictionary. If
                        False, the output will be serialized as a list of tuples (optional).
        :type path: str or None
        :type to_dict: bool
        :return: Returns the serialized file contents. The type of the return value depends on
                 the file extension and the `to_dict` flag. For JSON and YAML/YML files, it
                 returns either a dictionary or a list of tuples. For unsupported extensions
                 (e.g., 'ts'), it returns None. In case the file is not found, returns an
                 empty dictionary or list depending on the flag.
        :rtype: list[tuple[str, str]] | dict | None
        :raises ValueError: If an unsupported file extension is used.
        """
        file_path = path if isinstance(path, Path) else path if path else Path(self.path)
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
        """
        Processes and translates JSON language files for given language(s), and saves the translated
        content to specified output directory. Language files are handled either from a provided
        file or a list of them. Also ensures that existing translations are utilized unless
        `force` or `overwrite` options are enabled.

        :param lang_work: A list or single string representing the target language(s) for translation.
        :param lang_file: The path of the language file used as a basis for translation.
        :param output_dir: The directory where the translated JSON files will be stored.
        :param force: A boolean flag to force translation even if a previous translation exists.
        :param overwrite: A boolean flag to overwrite previously translated content.
        :return: None
        """
        base_data = self.extract_parse_file(to_dict=True)
        # if not isinstance(lang_work, list):
        #     lang_work = [lang_work]
        lang_work = [lang_work] if isinstance(lang_work, str) else lang_work  # Asegurar que sea una lista

        # path_output = Path(output_dir) if output_dir else self.translations_dir
        # path_output.mkdir(parents=True, exist_ok=True)

        output_path = Path(output_dir) if output_dir else self.translations_dir
        output_path.mkdir(parents=True, exist_ok=True)

        # for lang in lang_work:
        #     log.info(f'Traduciendo al idioma: {lang}')
        #     translated: List[Tuple[str, str]] = []
        #     output_file = path_output / f"{lang}.json"
        #
        #     # Se intenta leer el archivo traducido previamente, si existe
        #     try:
        #         new_data = self.extract_parse_file(output_file, to_dict=True)
        #     except Exception as e:
        #         log.info(f"No se pudo leer {output_file}, se creará uno nuevo. Error: {e}")
        #         new_data = {}
        #
        #     for key, base_value in base_data.items():
        #         out_value = new_data.get(key)
        #         # Si no hay traducción previa o se indica forzar/overwrite, se traduce
        #         if out_value is None or overwrite or force:
        #             log.debug(f"Traduciendo la clave: {key} (traducción previa: {out_value})")
        #             try:
        #                 translated_text = self.api.translate(base_value, lang_file, lang)
        #             except Exception as e:
        #                 log.error(f"Error al traducir {key}: {e}")
        #                 translated_text = None
        #             log.info(f'{key} ({lang_file} -> {lang}): {translated_text}')
        #             translated.append((key, translated_text))
        #         else:
        #             log.info(f'Usando traducción existente para {key}: {out_value}')
        #             translated.append((key, out_value))
        #
        #     json_instance = JSON(str(output_file))
        #     try:
        #         # Se guarda el resultado en el archivo de salida
        #         json_instance.save_json_file(json_instance.deserializar_json(translated))
        #     except Exception as e:
        #         log.error(f"Error al guardar {output_file}: {e}")
        #
        #     log.info('Finish convert languages packages......')
        for lang in lang_work:
            log.info(f'Traduciendo al idioma: {lang}')
            output_file = output_path / f"{lang}.json"
            translated_data = self._process_language_translation(lang, lang_file, base_data, output_file, force,
                                                                 overwrite)
            self._save_translated_data(output_file, translated_data)

        log.info('Finish converting language packages.')

    def worker(self, base: str = None, langs: list | str = None) -> None:
        """
        Processes language files for translation based on the provided base and language options.

        The function determines the correct language file to work with and identifies the valid
        languages for translation. It utilizes the class attributes and provided arguments to
        select the necessary configurations. If valid settings are not provided or the file format
        is unsupported, it logs an appropriate error message.

        :param base: Optional base language file to use for translation. If not provided, defaults
                     are determined based on the instance's attributes.
        :type base: str, optional
        :param langs: A list or a single string specifying the target languages for translation.
                      Only languages supported by the instance will be considered.
        :type langs: list or str, optional
        :return: None is returned if there are no valid languages for translation or if an
                 unsupported file format is provided.
        :rtype: None
        """
        lang_file = (
                base
                or getattr(self.args, 'base', None)
                or None
        )

        if langs is None:
            log.info("Detectando idioma")
            with open(self.path, 'r') as f:
                lang_file = self.api.detect_language(f.read())
                log.warning("Idioma detectado: " + lang_file)

        lang_work = self._get_target_languages(langs, lang_file)

        if not lang_work:
            log.error("No se especificaron idiomas válidos para trabajar.")

        if self.ext.lower() == 'json':
            output_dir = getattr(self.args, 'output', None) or self.translations_dir
            self.json_worker(lang_work, lang_file, output_dir, self.args.force, self.args.overwrite)
        else:
            log.error(
                f"Formato no soportado {self.ext}. Notificar al administrador (waltercunbustamante@gmail.com)")
        # return None
