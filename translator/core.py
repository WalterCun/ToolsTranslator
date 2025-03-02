#!/usr/bin/env python3
""" core.py """

import json
import logging
from pathlib import Path

from api.translate_api import LibreTranslate
from config_logging import config_logging

log = logging.getLogger(__name__)
config_logging(log, logging.INFO)


class Translator:
    """
    Provides functionality to manage and translate text into multiple languages using JSON files.

    This class facilitates working with multilingual translator by storing them in JSON
    files. It allows adding translator, switching languages, looking up translator
    by keys, and handles fallback to a default language if a translation for the current
    language is not found.

    Attributes:
        translations_dir (Path): Directory where translation files are stored.
        default_lang (str): Default language code.
        current_lang (str): Currently selected language code.
    """
    language_support: list = []

    def __init__(self, translations_dir: Path, default_lang="es", **kwargs):
        """
        Inicializa el traductor con un directorio de almacenamiento y un idioma predeterminado.

        :param translations_dir: Directorio donde se almacenan los archivos de traducción.
        :param default_lang: Idioma predeterminado.
        """
        self.api = LibreTranslate()
        self.meta = kwargs.get('meta', {})

        self.translations_dir = Path(translations_dir)

        self.default_lang = default_lang
        self.current_lang = default_lang

        # Crear el directorio de traducciones si no existe
        self.translations_dir.mkdir(parents=True, exist_ok=True)
        self.__get_languages_supported()
        self.dict_trans = self._load_translations(default_lang)

    def __get_languages_supported(self):
        self.language_support = self.api.get_supported_languages(self.current_lang)
        if self.language_support:
            self.language_support.append('auto')

    def _validate_lang(self, lang):
        if lang not in self.language_support and lang != 'auto':
            return False
        return True

    def _get_translation_file(self, lang):
        """
        Obtiene el nombre del archivo JSON para un idioma específico.

        :param lang: Código del idioma (e.g., 'en', 'es').
        :return: Ruta al archivo de traducción.
        """
        return self.translations_dir / f"{lang}.json"

    def _load_translations(self, lang) -> dict:
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

    def _save_translations(self, lang, translations):
        """
        Guarda las traducciones en un archivo JSON específico.

        :param lang: Código del idioma.
        :param translations: Diccionario de traducciones a guardar.
        """

        file_path = self._get_translation_file(lang)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)

    def add_trans(self, key, lang, value):
        """
        Agrega una traducción para una clave en un idioma específico.

        :param key: La clave identificadora de la traducción.
        :param lang: El idioma de la traducción (e.g., 'en', 'es', 'fr').
        :param value: El texto traducido.
        """

        log.info(f'Obtener archivo lang({lang})')
        translations = self._load_translations(lang)
        log.info(f'Obteniendo traduccion({key})')
        translations[key] = value
        log.info(f'Guardando traduccion >> {key}: {translations}')
        self._save_translations(lang, translations)

    def set_language(self, lang):
        """
        Establece el idioma actual para las traducciones.

        :param lang: El idioma que se usará (e.g., 'en', 'es').
        """
        if not self._validate_lang(lang):
            raise ValueError(
                f"Invalid language code: {lang}. Supported languages: {', '.join(self.language_support)}")
        self.dict_trans = self._load_translations(lang)
        self.current_lang = lang

    def translate(self, key):
        """
        Traduce una clave al idioma actual. Si no encuentra una traducción,
        intenta usar el idioma predeterminado. Si tampoco existe, devuelve un mensaje por defecto.

        :param key: La clave a traducir.
        :return: La traducción correspondiente o un mensaje predeterminado.
        """
        # Intentar traducir en el idioma actual
        translation = self.dict_trans.get(key)
        if translation:
            return translation

        # Si no se encuentra, intentar traducir en el idioma predeterminado
        if self.current_lang != self.default_lang:
            translation = self._load_translations(self.default_lang)
            translation = translation.get(key)
            if translation:
                return translation

        # Si no hay traducción, devolver un mensaje predeterminado
        return "No implement Translation"

    # -----------------------------------------------------------------------------------------------------------------

    def auto_translate(self, base_file: str = None, langs: list or str = None, force: bool = False):
        """
        Translates the provided text into multiple languages based on the input parameters.

        This method allows translation of text into supported languages. It has
        an optional parameter to override the existing language list if required.
        The function emits logs related to unsupported languages and processes
        only the supported ones.

        Parameters:
            base: str
                The base language of the text to be translated. Defaults to 'en'.
            langs: list
                A list of target languages for translation. If None, this parameter
                will not be used.
            force: bool
                A flag that specifies whether to force translation even if no
                languages are explicitly specified. Defaults to False.

        Raises:
            No specific exceptions are raised by this method, but it relies on the
            logging mechanism to provide information about unsupported languages
            or possible actions taken internally.

        Returns:
            None
        """
        limpiar_langs = None
        no_support = None
        _langs = None

        if isinstance(langs, str) and langs == 'all':
            _langs = self.language_support
        elif isinstance(langs, list):
            no_support_base = [item for item in [self.current_lang] if item not in self.language_support]
            print('no_support_base: ', no_support_base)

            if no_support_base:
                log.error(f"El idioma base no soportado {no_support_base}")
                return
            no_support = [item for item in langs if item not in self.language_support]
            limpiar_langs = None
            print('no_support: ', no_support)
            if no_support:
                log.info(f"No se encuentra soporte para {no_support}")
                limpiar_langs = [item for item in langs if item in self.language_support]
                log.info(f"Limpiando lenguajes no soportados")

        lang_work = limpiar_langs or no_support or _langs
        log.info(f"lenguajes a trabajar {lang_work}")

        base_data = self._load_translations(self.current_lang)
        for lang in lang_work:
            work = self._load_translations(lang)
            for bkey, btext in base_data.items():
                if (not work.get(bkey) and bkey not in work.keys()) or force:
                    translated = self.api.translate(btext, self.current_lang, lang)
                    self.add_trans(bkey, lang, translated)
                    log.info(f"AutoTraducción de llave {bkey} >> {translated}")

    #
    def __getattr__(self, key):
        """
        Permite acceder a las claves de traducción como si fueran atributos de la clase.

        :param key: La clave a traducir.
        :return: La traducción correspondiente o un mensaje predeterminado.
        """
        log.info(f'Obteniendo atributo >> {key}')
        return self.translate(key)

#
# if __name__ == '__main__':
#     translate = Translator(Path('.'))
#     print(translate.greetings)
#     translate.set_language("es")
#     print(translate.greetings)
#
#     translate.auto_translate("es", ["en"])
