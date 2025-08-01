#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/core/translate.py """
import json
import logging
from pathlib import Path
from typing import Dict

from translator.config import settings
from translator.api.translate_api import LibreTranslate


# config_logging(log, logging.INFO)

class Translator:
    """
        Provides functionality to manage and translate text into multiple languages using JSON files.

        This class facilitates working with multilingual translator by storing them in JSON
        files. It allows adding translator, switching languages, looking up translator
        by keys, and handles fallback to a default language if a translation for the current
        language is not found.

        Attributes:
            translations_dir (Path): Directory where translation files are stored.
            _current_lang (str): Currently selected language code.
    """

    def __init__(self, translations_dir: Path = settings.BASE_DIR / 'langs', default_lang="en"):
        self.api = LibreTranslate()

        self.translations_dir = Path(translations_dir)
        self.translations_dir.mkdir(parents=True, exist_ok=True)

        self._current_lang = default_lang
        self.dict_trans = {}

        # Crear el directorio de traducciones si no existe
        self.language_support = list(self.api.get_supported_languages(default_lang, to_list=True))

        if self.language_support:
            self.language_support.append('auto')

        self.log = logging.getLogger(__name__)

        self.dict_trans = self._load_translations(default_lang)

    @property
    def lang(self):
        """
        Represents a language property accessor.

        The `lang` property is designed to retrieve the current language setting.
        This property provides a thread-safe mechanism for accessing the value of
        the private `_current_lang` attribute. It maintains immutability by ensuring
        that no external changes can be made directly to the attribute value.

        :return: The current language setting.
        :rtype: Any
        """
        return self._current_lang

    @lang.setter
    def lang(self, value):
        """
        Sets the language for the application by checking if the provided language
        code is valid. If the language code is valid, the method updates the
        current language, reloads dictionary translations, and sets the language
        code. Raises a `ValueError` if the provided language code is not supported.

        :param value: The new language code to set.
        :type value: str

        :raises ValueError: If the provided language code is not supported.
        """
        if not self._validate_lang(value):
            raise ValueError(
                f"Invalid language code: {value}. Supported languages: {', '.join(self.language_support)}")
        self.dict_trans = self._load_translations(value)
        self._current_lang = value

    # def __get_languages_supported(self):
    #     """Get supported languages from the API"""
    #     languages = self.api.get_supported_languages(self.lang)
    #     if languages:
    #         languages.append('auto')
    #     return languages

    def _validate_lang(self, lang) -> bool:
        """
        Validates whether the provided language is supported or set to 'auto'.

        This method checks if the given language parameter matches one of the
        supported languages or is explicitly set to 'auto'. It ensures that the
        input language is correctly validated for compatibility within the
        application's configuration.

        :param lang: The language code to validate.
        :type lang: str
        :return: A boolean indicating whether the language is valid or set to 'auto'.
        :rtype: bool
        """
        if lang not in self.language_support:
            return False
        return True

    def _get_translation_file(self, lang) -> Path:
        """
        Obtiene el nombre del archivo JSON para un idioma específico.

        :param lang: Código del idioma (e.g., 'en', 'es').
        :return: Ruta al archivo de traducción.
        """
        return self.translations_dir / f"{lang}.json"

    def _load_translations(self, lang) -> Dict:
        """
        Carga las traducciones de un archivo JSON específico.

        :param lang: Código del idioma.
        :return: Diccionario con las traducciones cargadas.
        """
        if not self._validate_lang(lang):
            raise ValueError(
                f"Invalid language code: {lang}. Supported languages: {', '.join(self.language_support)}")

        file_path = self._get_translation_file(lang)
        if file_path.exists():
            with file_path.open(encoding="utf-8") as file:
                return json.load(file)
        else:
            return {}

    # def _load_struct_translate(self, base_file: str = None) -> None:
    #     """
    #     Loads translation structure based on the file type and extracts the relevant content. Supports specific
    #     extensions like `json`, and processes content accordingly. Other extensions or unsupported formats
    #     will raise a ValueError.
    #
    #     :param base_file: Path to the base file for processing. Defaults to None, meaning that path will
    #                       be retrieved from the meta data if not explicitly provided.
    #     :type base_file: Optional[str]
    #     :return: None
    #     """
    #     if self.meta.get('ext') == 'json':
    #         json_data = JSON.get_content_json_file(base_file or self.meta.get('path'))
    #         extracted_texts = JSON.serializer_json(json_data)
    #         for path, text in extracted_texts:
    #             print(f"Ruta: {path} -> {text}")
    #     elif self.meta.get('ext') == 'yaml':
    #         pass
    #     elif self.meta.get('ts') == 'ts' or self.meta.get('name') == 'i18n.ts':
    #         pass
    #     else:
    #         raise ValueError(f"Formato no soportado {self.meta.get('ext')}")

    def _save_translations(self, lang, translations) -> None:
        """
        Guarda las traducciones en un archivo JSON específico.

        :param lang: Código del idioma.
        :param translations: Diccionario de traducciones a guardar.
        """

        file_path = self._get_translation_file(lang)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)

    def add_trans(self, key: str, lang: str, value: str, force: bool = False) -> None:
        """
        Agrega una traducción para una clave en un idioma específico.

        :param force:
        :param key: La clave identificadora de la traducción.
        :param lang: El idioma de la traducción (e.g., 'en', 'es', 'fr').
        :param value: El texto traducido.
        """

        self.log.info(f'Obtener archivo lang({lang})')
        translations = self._load_translations(lang)
        self.log.info(f'Obteniendo traduccion({key})')
        translations[key] = value
        self.log.info(f'Guardando traduccion >> {key}: {translations}')
        self._save_translations(lang, translations)

    def _translate(self, key) -> str:
        """
        Traduce una clave al idioma actual. Si no encuentra una traducción,
        intenta usar el idioma predeterminado. Si tampoco existe, devuelve un mensaje por defecto.

        :param key: La clave a traducir.
        :return: La traducción correspondiente o un mensaje predeterminado.
        """
        # Intentar traducir en el idioma actual
        translation = self.dict_trans.get(key, None)
        if translation:
            return translation

        # Si no se encuentra, intentar traducir en el idioma predeterminado

        translation = self._load_translations(self.lang)
        translation = translation.get(key)
        if translation:
            return translation

        # Si no hay traducción, devolver un mensaje predeterminado
        self.add_trans(key, self.lang, "No implement Translation")
        return "No implement Translation"

    def __getattr__(self, key) -> str:
        """
        Permite acceder a las claves de traducción como si fueran atributos de la clase.

        :param key: La clave a traducir.
        :return: La traducción correspondiente o un mensaje predeterminado.
        """
        self.log.info(f'Obteniendo atributo >> {key}')
        return self._translate(key)


if __name__ == '__main__':
    translate = Translator()
    print(translate.lang)
    print(translate.greetings)
    translate.lang = "es"
    print(translate.lang)
    print(translate.greetings)

    # translate.auto_translate("es", ["en"])
