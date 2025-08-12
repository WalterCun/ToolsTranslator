#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/core/translate.py """
import json
import hashlib
import os
import logging
from pathlib import Path
from typing import Dict, Union, Optional, Literal, Tuple

from translator.config import settings
from translator.api.translate_api import LibreTranslate


class AuxiliarTranslationProxy:
    """
    Proxy para acceder a traducciones anidadas usando notación de puntos.

    Permite acceder a claves de diccionarios anidados como si fueran atributos.
    Este proxy solo resuelve el valor cuando se convierte a cadena (str) o
    cuando el nodo es terminal.

    Ejemplo:
        >>> from translator.core.translate import Translator
        >>> t = Translator(default_lang="es")
        >>> t.add_trans("app.header.title", "es", "Título", nested=True)
        >>> str(t.app.header.title)
        'Título'
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
                new_proxy._terminal_value = self.translator.get_translation(full_key)
                return new_proxy

    def _get_nested_value(self, data: dict, key_path: str):
        """
        Obtiene un valor de un diccionario anidado usando una ruta separada por puntos.

        :param data: Diccionario donde buscar.
        :param key_path: Ruta de claves separadas por puntos.
        :return: Valor encontrado o None si no existe.
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
        Check if there could be potential nested keys based on the existing structure.

        :param data: Dictionary to search in
        :param key_path: a Key path to check
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
            return self.translator.get_translation(self.parent_key)

        return self.DEFAULT_MISSING_KEY_MESSAGE

    def __repr__(self) -> str:
        """
        Return a string representation of the proxy.
        """
        return self.__str__()


class Translator:
    """
    Gestor de traducciones basado en archivos JSON con soporte para claves anidadas.

    Esta clase permite:
    - Cargar y guardar archivos de traducción por idioma.
    - Agregar traducciones (planas o anidadas mediante notación con puntos).
    - Cambiar el idioma activo y obtener textos traducidos.
    - Opcionalmente crear claves faltantes con un mensaje por defecto.

    Atributos principales:
    - translations_dir (Path): Directorio donde se almacenan los archivos de traducción.
    - lang (str): Idioma actual.

    Ejemplo de uso básico:
        >>> from translator.core.translate import Translator
        >>> t = Translator(default_lang="es")
        >>> t.add_trans("app.header.title", "es", "Título", nested=True)
        >>> t.lang = "es"
        >>> t.get_translation("app.header.title")
        'Título'

    Acceso anidado mediante atributos (proxy):
        >>> str(t.app.header.title)
        'Título'
    """

    DEFAULT_MISSING_KEY_MESSAGE = "Key no Implemented"

    def __init__(self, translations_dir: Path = settings.BASE_DIR / 'langs', default_lang="en",
                 validate_or_correct_connection: bool = False, nested: Optional[bool] = None,
                 auto_add_missing_keys: Optional[bool] = None,
                 validation_mode: Literal['mtime', 'hash'] = "mtime"):
        """
        Inicializa el gestor de traducciones.

        :param translations_dir: Directorio donde se almacenan los archivos JSON de traducción.
        :param default_lang: Idioma inicial a cargar (por ejemplo, "es", "en").
        :param validate_or_correct_connection: Si es True, valida/ayuda a iniciar el servicio LibreTranslate vía Docker.
        :param nested: Control global para agregar claves anidadas cuando contienen puntos (True) o planas (False). Si es None, se decide por cada llamada.
        :param auto_add_missing_keys: Si es True, crea claves faltantes con un mensaje por defecto cuando se consultan.
        :param validation_mode: Modo de validación de caché de archivo ("mtime" por fecha de modificación o "hash" por hash MD5).
        :raises ValueError: Si validation_mode no es "mtime" ni "hash" o si el idioma por defecto no es soportado.
        """
        # Inicializar logger
        self.log = logging.getLogger(__name__)
        # validar y cargar modo de validacion de archivo de traducciones
        if validation_mode not in {"mtime", "hash"}:
            raise ValueError('validation_mode debe ser "mtime" o "hash"')
        self.validation_mode = validation_mode
        # Inicializar directorio de traducciones
        self.translations_dir = Path(translations_dir)
        # Crear directorio de traducciones si no existe
        self.translations_dir.mkdir(parents=True, exist_ok=True)
        # Cargar idioma por default
        self._current_lang = default_lang
        # Inicializar diccionario de traducciones
        self.dict_trans = {}

        # Cache: { lang: (data, marker) } -> marker = mtime o hash
        self._cache: Dict[str, Tuple[Dict, Union[float, str]]] = {}

        # Opciones de anidamiento de claves
        self._global_nested = nested
        # Opciones de agregar claves faltantes automaticamente
        self._global_auto_add_missing_keys = auto_add_missing_keys

        # Inicializar api de traduccion
        self.api = LibreTranslate(connection_validate=validate_or_correct_connection)
        # Inicializar lista de idiomas soportados
        self.language_support = self.api.get_supported_languages(default_lang, to_list=True)
        if self.language_support:
            self.language_support.append('auto')
        # Cargar traducciones por defecto
        self.dict_trans = self._load_translations(default_lang)

    @property
    def lang(self):
        """
        Propiedad que devuelve el idioma actual.

        Esta propiedad expone el código de idioma que está en uso en el traductor
        (por ejemplo, "es", "en"). Se usa para determinar de qué archivo JSON
        se leen las traducciones al consultar claves.

        :return: Código del idioma actual.
        :rtype: str
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
        :type value: Str

        :raises ValueError: If the provided language code is not supported.
        """
        if not self._validate_lang(value):
            raise ValueError(
                f"Invalid language code: {value}. Supported languages: {', '.join(self.language_support)}")
        self.dict_trans = self._load_translations(value)
        self._current_lang = value

    @property
    def nested(self):
        """
        Control global de anidamiento de claves.

        Si es True, al agregar traducciones con claves que contienen puntos
        se crearán estructuras anidadas. Si es False, se tratarán como claves planas.
        Si se deja en None, se decide por cada llamada a add_trans.

        :return: Valor actual de la preferencia global de anidamiento.
        :rtype: Optional[bool]
        """
        return self._global_nested

    @nested.setter
    def nested(self, value: bool):
        self._global_nested = value

    @property
    def auto_add_missing_keys(self):
        """
        Control global para creación automática de claves faltantes.

        Si es True, cuando se solicite una clave inexistente mediante get_translation
        o el proxy anidado, se insertará automáticamente en el archivo del idioma
        actual con el valor por defecto "Key no Implemented".

        :return: Estado actual de la creación automática.
        :rtype: Optional[bool]
        """
        return self._global_auto_add_missing_keys

    @auto_add_missing_keys.setter
    def auto_add_missing_keys(self, value: bool):
        self._global_auto_add_missing_keys = value

    # -----------------------------------------------------------------------------------------------------------------
    def _validate_lang(self, lang) -> bool:
        """
        Valida si el idioma proporcionado está soportado (o es 'auto').

        Verifica que el código de idioma exista en la lista de idiomas soportados
        por la API configurada. Devuelve True si es válido o si es 'auto'.

        :param lang: Código de idioma a validar (por ejemplo, 'es', 'en', 'auto').
        :return: True si el idioma es válido, False en caso contrario.
        :rtype: bool
        """
        return lang in self.language_support

    def _get_translation_file(self, lang) -> Path:
        """
        Obtiene el nombre del archivo JSON para un idioma específico.

        :param lang: Código del idioma (e.g., 'en', 'es').
        :return: Ruta al archivo de traducción.
        """
        return self.translations_dir / f"{lang}.json"

    def _get_file_marker(self, file_path: Path) -> Optional[Union[float, str]]:
        """Obtiene mtime o hash del archivo según el modo."""
        if not file_path.exists():
            return None
        if self.validation_mode == "mtime":
            return os.path.getmtime(file_path)
        else:  # hash mode
            hasher = hashlib.md5()
            with file_path.open("rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()

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
        marker = self._get_file_marker(file_path)

        if lang in self._cache:
            cached_data, cached_marker = self._cache[lang]
            if cached_marker == marker:
                return cached_data  # Cache válido

        # Si llegamos aquí, es porque no hay cache o el archivo cambió
        if not file_path.exists():
            self._cache[lang] = ({}, marker)
            return {}

        with file_path.open(encoding="utf-8") as file:
            data = json.load(file)
            self._cache[lang] = (data, marker)
            return data

    def _save_translations(self, lang, translations) -> None:
        """
        Guarda las traducciones en un archivo JSON específico.

        :param lang: Código del idioma.
        :param translations: Diccionario de traducciones a guardar.
        """

        file_path = self._get_translation_file(lang)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)

    @staticmethod
    def _set_nested_value(data: dict, key_path: str, value: str) -> dict:
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

    def add_trans(self, key: str, lang: str, value: str, force: bool = False, nested: Optional[bool] = None) -> None:
        """
        Agrega una traducción para una clave en un idioma específico.
        Soporta claves anidadas cuando nested=True.

        Precedencia para "nested":
        - Valor del métod (True/False) si no es None
        - Valor global del constructor (self._global_nested) si fue provisto
        - Comportamiento legacy por defecto: True

        :param key: La clave identificadora de la traducción (puede usar puntos para anidamiento).
        :param lang: El idioma de la traducción (e.g., 'en', 'es', 'fr').
        :param value: El texto traducido.
        :param force: Si fuerza la sobrescritura de traducciones existentes.
        :param nested: Si usa estructura anidada para claves con puntos (True) o clave plana (False). Si es None, se
                       usa la configuración global o el valor por defecto (True).
        """
        self.log.info(f'Obtener archivo lang({lang})')
        translations = self._load_translations(lang)

        use_nested = nested or self._global_nested

        if use_nested and AuxiliarTranslationProxy.NESTED_KEY_SEPARATOR in key:
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
            if use_nested and AuxiliarTranslationProxy.NESTED_KEY_SEPARATOR in key:
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

    @staticmethod
    def _get_nested_value(data: dict, key_path: str):
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

    def _translate(self, key: str, auto_add_missing: Optional[bool] = None) -> str:
        """
        Traduce una clave al idioma actual SOLAMENTE.
        No busca en idiomas fallback para mostrar correctamente cuando una clave no está implementable.

        Precedencia para "auto_add_missing":
        - Valor del método (True/False) si no es None
        - Valor global del constructor (self._global_auto_add_missing_keys) si fue provisto
        - Comportamiento legacy por defecto: False

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

        # Resolver comportamiento efectivo para auto-add
        do_auto_add = auto_add_missing if auto_add_missing is not None else (
            getattr(self, '_global_auto_add_missing_keys', None)
            if getattr(self, '_global_auto_add_missing_keys', None) is not None else False
        )

        # Si no hay traducción en el idioma actual, agregar mensaje por defecto
        if do_auto_add:
            self.add_trans(key, self.lang, self.DEFAULT_MISSING_KEY_MESSAGE, nested=None)

        return self.DEFAULT_MISSING_KEY_MESSAGE

    # -----------------------------------------------------------------------------------------------------------------

    def get_translation(self, key: str, auto_create: Optional[bool] = None) -> str:
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

# if __name__ == '__main__':
#     trans = Translator()
#     trans.lang = "es"
#
#     trans.nested = False
#     trans.add_trans("user.messages.welcome", "es", "Bienvenido")
#     trans.add_trans("user.messages.bay", "es", "Adios", nested=True)
#
#     trans.auto_add_missing_keys = False
#     trans.add_trans("user.messages.baby", "es", "Bebe")
#
#     trans.get_translation("user.messages.babies", auto_create=True)
#     print(trans.user.messages.boyas)
#     trans.auto_add_missing_keys = True
#     print(trans.user.messages.boys)
