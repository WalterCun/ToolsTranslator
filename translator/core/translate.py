#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/core/translate.py """
import json
import logging
from pathlib import Path
from typing import Dict, Union

from translator.config import settings
from translator.api.translate_api import LibreTranslate


class AuxiliarTranslationProxy:
    """
    Proxy class to handle nested translation access using dot notation.
    Allows accessing nested dictionary keys as attributes.
    """
    NESTED_KEY_SEPARATOR = "."
    DEFAULT_MISSING_KEY_MESSAGE = "Key no Implemented"

    def __init__(self, translator: 'Translator', parent_key: str = ""):
        self.translator = translator
        self.parent_key = parent_key
        self._is_terminal = False  # Flag para saber si este proxy representa un valor terminal

    def __getattr__(self, key: str):
        """
        Handle nested attribute access for translations.

        :param key: The key to access
        :return: NestedTranslationProxy for further nesting or translated string
        """
        full_key = f"{self.parent_key}{self.NESTED_KEY_SEPARATOR}{key}" if self.parent_key else key

        # Crear un nuevo proxy para la clave completa
        new_proxy = AuxiliarTranslationProxy(self.translator, full_key)

        # Verificar si existe como estructura anidada o valor final
        nested_value = self._get_nested_value(self.translator.dict_trans, full_key)

        if isinstance(nested_value, dict):
            # Es una estructura anidada, devolver proxy para continuar
            return new_proxy
        elif nested_value is not None:
            # Es un valor final, marcar el proxy como terminal
            new_proxy._is_terminal = True
            new_proxy._terminal_value = str(nested_value)
            return new_proxy
        else:
            # No existe, verificar si podría existir estructura anidada
            if self._could_have_nested_structure(self.translator.dict_trans, full_key):
                # Podría tener estructura anidada, continuar con proxy
                return new_proxy
            else:
                # No hay estructura posible, marcar como terminal con mensaje por defecto
                new_proxy._is_terminal = True
                new_proxy._terminal_value = self.translator._translate(full_key)
                return new_proxy

    def _get_nested_value(self, data: dict, key_path: str):
        """
        Get value from a nested dictionary using a dot-separated key path.

        :param data: Dictionary to search in
        :param key_path: Dot-separated key path
        :return: Value if found, None otherwise
        """
        keys = key_path.split(self.NESTED_KEY_SEPARATOR)
        current_value = data

        for key in keys:
            if isinstance(current_value, dict) and key in current_value:
                current_value = current_value[key]
            else:
                return None

        return current_value

    def _could_have_nested_structure(self, data: dict, key_path: str) -> bool:
        """
        Check if there could be potential nested keys based on existing structure.

        :param data: Dictionary to search in
        :param key_path: Key path to check
        :return: True if there could be potential nested matches
        """
        # Obtener la primera parte del key path
        keys = key_path.split(self.NESTED_KEY_SEPARATOR)

        # Verificar si existe la primera clave como diccionario
        current_value = data
        for key in keys:
            if isinstance(current_value, dict) and key in current_value:
                current_value = current_value[key]
                if isinstance(current_value, dict):
                    return True
            else:
                break

        # Verificar si hay claves planas que empiecen con este path
        return any(k.startswith(key_path + self.NESTED_KEY_SEPARATOR) for k in data.keys() if isinstance(k, str))

    def __str__(self) -> str:
        """
        Convert proxy to string by returning the terminal value or translating.
        """
        if hasattr(self, '_is_terminal') and self._is_terminal:
            return getattr(self, '_terminal_value', self.DEFAULT_MISSING_KEY_MESSAGE)

        if self.parent_key:
            return self.translator._translate(self.parent_key)

        return self.DEFAULT_MISSING_KEY_MESSAGE

    def __repr__(self) -> str:
        """
        Return a string representation of the proxy.
        """
        return self.__str__()


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

    DEFAULT_MISSING_KEY_MESSAGE = "Key no Implemented"

    def __init__(self, translations_dir: Path = settings.BASE_DIR / 'langs', default_lang="en",
                 validate_or_correct_connection: bool = False):
        self.api = LibreTranslate(connection_validate=validate_or_correct_connection)

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

    def _save_translations(self, lang, translations, force=False) -> None:
        """
        Guarda las traducciones en un archivo JSON específico.

        :param lang: Código del idioma.
        :param translations: Diccionario de traducciones a guardar.
        :param force: Parámetro opcional para compatibilidad
        """

        file_path = self._get_translation_file(lang)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)

    def _set_nested_value(self, data: dict, key_path: str, value: str) -> dict:
        """
        Establece un valor en un diccionario anidado usando una ruta de claves separadas por puntos.

        :param data: Diccionario donde establecer el valor
        :param key_path: Ruta de claves separadas por puntos
        :param value: Valor a establecer
        :return: Diccionario modificado
        """
        keys = key_path.split(AuxiliarTranslationProxy.NESTED_KEY_SEPARATOR)
        current_dict = data

        # Navegar hasta la penúltima clave, creando diccionarios si es necesario
        for key in keys[:-1]:
            if key not in current_dict:
                current_dict[key] = {}
            elif not isinstance(current_dict[key], dict):
                # Si existe pero no es un diccionario, lo convertimos a diccionario
                current_dict[key] = {}
            current_dict = current_dict[key]

        # Establecer el valor en la última clave
        final_key = keys[-1]
        current_dict[final_key] = value

        return data

    def add_trans(self, key: str, lang: str, value: str, force: bool = False, nested: bool = True) -> None:
        """
        Agrega una traducción para una clave en un idioma específico.
        Soporta claves anidadas cuando nested=True.

        :param key: La clave identificadora de la traducción (puede usar puntos para anidamiento).
        :param lang: El idioma de la traducción (e.g., 'en', 'es', 'fr').
        :param value: El texto traducido.
        :param force: Si fuerza la sobrescritura de traducciones existentes.
        :param nested: Si usa estructura anidada para claves con puntos (True) o clave plana (False).
        """
        self.log.info(f'Obtener archivo lang({lang})')
        translations = self._load_translations(lang)

        if nested and AuxiliarTranslationProxy.NESTED_KEY_SEPARATOR in key:
            # Usar estructura anidada
            self.log.info(f'Agregando traducción anidada para clave: {key}')
            translations = self._set_nested_value(translations, key, value)
        else:
            # Usar clave plana (comportamiento original)
            self.log.info(f'Obteniendo traduccion({key})')

            # Si force=False y ya existe, no sobrescribir
            if not force and key in translations:
                self.log.info(f'Traducción ya existe para {key}: {translations[key]}')
                return

            translations[key] = value

        self.log.info(f'Guardando traduccion >> {key}: {value}')
        self._save_translations(lang, translations)

        # Actualizar el diccionario en memoria si es el idioma actual
        if lang == self._current_lang:
            if nested and AuxiliarTranslationProxy.NESTED_KEY_SEPARATOR in key:
                self.dict_trans = self._set_nested_value(self.dict_trans, key, value)
            else:
                self.dict_trans[key] = value

    def add_nested_trans(self, key_path: str, lang: str, value: str, force: bool = False) -> None:
        """
        Métod de conveniencia para agregar traducciones anidadas.

        :param key_path: Ruta de claves separadas por puntos (ej: "user.messages.welcome")
        :param lang: Código del idioma
        :param value: Valor de la traducción
        :param force: Si fuerza la sobrescritura
        """
        self.add_trans(key_path, lang, value, force, nested=True)

    def add_flat_trans(self, key: str, lang: str, value: str, force: bool = False) -> None:
        """
        Métod de conveniencia para agregar traducciones con clave plana.

        :param key: Clave de traducción (se guardará tal como está, incluso con puntos)
        :param lang: Código del idioma
        :param value: Valor de la traducción
        :param force: Si fuerza la sobrescritura
        """
        self.add_trans(key, lang, value, force, nested=False)

    def _get_nested_value(self, data: dict, key_path: str):
        """
        Obtiene un valor de un diccionario anidado usando una ruta de claves separadas por puntos.

        :param data: Diccionario en el que buscar
        :param key_path: Ruta de claves separadas por puntos
        :return: Valor si se encuentra, None en caso contrario
        """
        keys = key_path.split(AuxiliarTranslationProxy.NESTED_KEY_SEPARATOR)
        current_value = data

        for key in keys:
            if isinstance(current_value, dict) and key in current_value:
                current_value = current_value[key]
            else:
                return None

        return current_value

    def _translate(self, key: str, auto_add_missing: bool = False) -> str:
        """
        Traduce una clave al idioma actual SOLAMENTE.
        No busca en idiomas fallback para mostrar correctamente cuando una clave no está implementable.

        :param key: La clave a traducir (puede incluir puntos para anidamiento).
        :param auto_add_missing: Si agregar automáticamente claves faltantes con mensaje por defecto.
        :return: La traducción correspondiente o un mensaje predeterminado.
        """
        # SOLO buscar en el idioma actual - no usar fallback

        # Intentar buscar la traducción usando el acceso anidado en el idioma actual
        translation = self._get_nested_value(self.dict_trans, key)
        if translation and not isinstance(translation, dict):
            return str(translation)

        # Intentar buscar la clave tal como está (compatibilidad con claves con puntos)
        direct_translation = self.dict_trans.get(key, None)
        if direct_translation and not isinstance(direct_translation, dict):
            return str(direct_translation)

        # Si no hay traducción en el idioma actual, agregar mensaje por defecto
        if auto_add_missing:
            self.add_trans(key, self.lang, self.DEFAULT_MISSING_KEY_MESSAGE)

        return self.DEFAULT_MISSING_KEY_MESSAGE

    def get_translation(self, key: str, auto_create: bool = False) -> str:
        """
        Métod público para obtener traducciones con control explícito sobre la creación de claves.

        :param key: La clave a traducir
        :param auto_create: Si crear automáticamente la clave si no existe
        :return: La traducción o mensaje por defecto
        """
        return self._translate(key, auto_add_missing=auto_create)

    def __getattr__(self, key: str):
        """
        Permite acceder a las claves de traducción como atributos, soportando acceso anidado.

        :param key: La clave a traducir.
        :return: AuxiliarTranslationProxy para acceso anidado o string para valores finales.
        """
        self.log.info(f'Obteniendo atributo >> {key}')

        # Siempre devolver un proxy que maneje la lógica
        return AuxiliarTranslationProxy(self, key)


if __name__ == '__main__':
    trans = Translator()
    trans.lang = "es"

    # Test con clave que existe en en.json pero no en es.json
    print(f"trans.user.messages.welcome = {trans.user.messages.welcome}")
