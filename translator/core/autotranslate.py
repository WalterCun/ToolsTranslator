#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" translator/core/autotranslate.py """

import logging
from argparse import Namespace
from pathlib import Path
from typing import Optional, Union, Dict, List

from translator.parses.tyaml import YAML
from translator.parses.tjson import JSON

from translator.utils import TranslateFile
from translator.utils.extract_info_file import extract_first_primitive_value

logging.basicConfig(
    level=logging.WARN,  # Establece el nivel mínimo de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="[%(asctime)s] - [%(name)s] - [%(levelname)s] -> %(message)s",  # Formato del log
    handlers=[
        logging.StreamHandler(),  # Enviar mensajes al terminal
    ]
)

log = logging.getLogger(__name__)


class AutoTranslate:
    """
    Handles file translation tasks with built-in language detection and API integration.

    This class is designed to facilitate the process of translating files in various languages
    while detecting the base language of the content. It ensures compatibility with translation
    APIs and streamlines tasks related to handling translations, including parsing and saving
    language files.

    :ivar api: Instance of the translation API used for managing translation operations.
    :type api: LibreTranslate
    :ivar language_support: List of supported languages for translation based on API response.
    :type language_support: List[str]
    :ivar fileTranslation: An object containing file metadata and content relevant for translation.
    :type file_translation: TranslateFile
    :ivar lang_work: The detected or selected working language(s) for translation.
    :type lang_work: Str or list[str]
    :ivar confidence: Confidence score for the detected language.
    :type confidence: Float
    :ivar args: Optional configuration parameters for translation settings.
    :type args: Namespace
    """

    def __init__(self, file_translation: TranslateFile, args: Namespace = Namespace(base=None)):
        """
        Initializes the class for handling file translation tasks with language detection
        and setup for translation API support. This class ensures that the file translation
        process is integrated with a language detection feature to provide insights
        and additional functionality.

        :param file_translation: An instance of the TranslateFile class that carries details
            of the file's content and related metadata necessary for processing the
            translation.
        :type file_translation: TranslateFile
        :param args: An instance of Namespace that provides configurable options
            such as the base language or other settings needed for customization.
            Defaults to a Namespace with a base of None.
        :type args: Namespace
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
                    return [lang for lang in
                            self.language_support] if self.args.overwrite else [lang for lang in self.language_support if
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
        Processes the translation for a specific language, using existing translations if available.

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

    def _save_translated_data(self, output_file: Path, translated_data: List[tuple[str, str]] or Dict[str,str]):
        """
        Saves translated data to a specified JSON output file. This function serializes
        the provided translated data and writes it to the target file path.

        :param output_file: Path instance representing the target file location for
            saving the serialized JSON data.
        :type output_file: Path

        :param translated_data: Container holding the translated data. It can either
            be a list of tuples where each tuple contains a key-value pair as
            (original_text, translated_text), or a dictionary with keys as the source
            texts and values as their corresponding translations.
        :type translated_data: List[tuple[str, str]] or Dict[str, str]

        :return: None
        """
        json_instance = JSON(str(output_file))
        try:
            json_instance.save_json_file(json_instance.deserializar_json(translated_data.items()))
        except Exception as e:
            log.error(f"Error al guardar {output_file}: {e}")

    def extract_parse_file(self, path: Optional[Path] = None, to_dict: bool = False) -> list[tuple[
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
        :type path: Str or None
        :type to_dict: bool
        :return: Returns the serialized file contents. The type of the return value depends on
                 the file extension and the `to_dict` flag. For JSON and YAML/YML files, it
                 returns either a dictionary or a list of tuples. For unsupported extensions
                 (e.g., 'ts'), it returns None. In case the file is not found, returns an
                 empty dictionary or list depending on the flag.
        :rtype: List[tuple[str, str]] | dict | None
        :raises ValueError: If an unsupported file extension is used.
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
            self._save_translated_data(output_file, translated_data)

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
