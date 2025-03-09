#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/api/translate_api.py """

import logging
from datetime import timedelta
from typing import Optional, Dict
from urllib.parse import urljoin

import requests
import requests_cache
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from translator.config import settings

log = logging.getLogger(__name__)

# Configuración de la caché usando SQLite (persistente)
requests_cache.install_cache(
    str(settings.BASE_DIR / "TranslateApi.db"),  # Nombre de la base de datos SQLite para la caché
    expire_after=timedelta(days=1)
)


class LibreTranslate:
    """
    Manages interactions with a LibreTranslate API instance, providing methods to translate
    text and retrieve supported languages.

    This class is designed to interface with a specified LibreTranslate API endpoint. It
    provides functionality to request the list of supported languages and perform text
    translations while handling errors and retries. The translations are done using HTTP
    POST requests. If the API responds with an error or the server is unreachable, the
    class includes retry logic to reattempt the request a specified number of times.
    Additionally, the supported language data is cached for efficient reuse.

    :ivar url_translate: The URL endpoint used for the translation API requests.
    :type url_translate: str
    :ivar url_languages: The URL endpoint used for retrieving supported languages.
    :type url_languages: str
    :ivar max_retries: The maximum number of retries for requests in case of failure.
    :type max_retries: int
    :ivar retry_delay: The delay in seconds between retry attempts for failed requests.
    :type retry_delay: int
    """

    def __init__(self, url: str = "http://localhost:5000/", max_retries=3, retry_delay=3):
        self.url_translate = urljoin(url, 'translate')
        self.url_languages = urljoin(url, 'languages')
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Configuramos una sesión para reutilizar conexiones y mejorar el rendimiento
        self.session = requests.Session()
        self.session.headers.update(settings.HEADERS)

        # Configuramos el retry utilizando HTTPAdapter y urllib3.util.Retry
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _request_supported_languages(self):
        """
        Request a list of supported languages from the specified API endpoint.

        This method sends a GET request to the URL stored in `self.url_languages`
        using the headers defined in `settings.HEADERS`. It handles HTTP errors
        by raising exceptions and clears the request cache in case of request
        failures.

        :return: A JSON object containing the supported languages.
        :rtype: dict
        :raises Exception: If an error occurs during the HTTP request.
        """
        log.info("Solicitando lista de idiomas soportados...")
        try:
            response = requests.get(self.url_languages, headers=settings.HEADERS)
            response.raise_for_status()  # Lanza un error si el código HTTP indica un fallo.
            return response.json()
        except requests.RequestException as e:
            requests_cache.clear()
            raise Exception(f"Error al realizar la solicitud: {str(e)}")

    def get_supported_languages(self, lang_base, to_list: bool = False):
        """
        Retrieves a list of supported languages for translation based on the base language provided.

        If the base language is matched in the response, it returns the list of target languages.
        Otherwise, if the base language is set to automatic detection ("auto"), it adds all
        available language codes to a set and finally returns them as a list.

        :param lang_base: Base language code to filter or retrieve available target languages.
                          Use "auto" for automatic detection of all available languages.
        :type lang_base: str
        :return: A list of target language codes if the base language is found or 'auto' is specified.
                 Returns an empty list if no supported languages are found or an error occurs.
        :rtype: list
        """
        try:
            response = self._request_supported_languages()
            languages: Dict = {}
            targets: Optional[list] = None
            for i in response:
                languages[i.get('name')] = i.get('code')  # Construimos el diccionario languages
                if lang_base == i.get('code'):  # Comprobamos si coincide con lang_base
                    targets = i.get('targets', [])
            if targets:
                languages = {k: v for k, v in languages.items() if v in targets}
            if to_list:
                return list(languages.values())
            return languages
        except Exception as e:
            log.error(f"Error al obtener idiomas: {str(e)}")
            return []

    def translate(self, text, source, target, retry=0):
        """
        Translates a given text from a source language to a target language using a remote
        translation API. This method handles retries if the API call fails and ensures
        the response is parsed correctly to extract the translated text.

        :param text: str
            The text to be translated.
        :param source: Optional[str]
            The source language code. If None or empty, the API will auto-detect the language.
        :param target: str
            The target language code to which the text needs to be translated.
        :param retry: int
            The current retry attempt count, used for managing retries on failure.

        :return: str
            Returns the translated text if successful. If the maximum retries are
            exceeded or an error occurs, an empty string is returned.
        """

        payload = {
            "q": text,
            "source": source or "auto",
            "target": target,
            "format": "text",
        }

        # while retry <= self.max_retries:
        #     try:
        #         with requests_cache.disabled():
        #             response = requests.post(self.url_translate, json=payload, headers=settings.HEADERS,
        #                                      timeout=self.retry_delay or 3)
        #             if response.status_code == 200:
        #                 translated_text = response.json().get("translatedText", "")
        #                 if not translated_text:
        #                     log.error("La respuesta del servidor no contiene la traducción.")
        #                 return translated_text
        #             else:
        #                 log.error(f"Error: {response.status_code}, {response.content}")
        #     except requests.RequestException as e:
        #         log.error(f"Excepción en la traducción: {str(e)}")
        #     retry += 1
        try:
            # with requests_cache.disabled():
            response = requests.post(self.url_translate, json=payload)
            if response.status_code == 200:
                translated_text = response.json().get("translatedText", "")
                if not translated_text:
                    log.error("La respuesta del servidor no contiene la traducción.")
                return translated_text
            else:
                log.error(f"Error: {response.status_code}, {response.content}")
        except requests.RequestException as e:
            log.error(f"Error en la traducción: {e}")
            return ""

# if __name__ == '__main__':
# lt = LibreTranslate()
# print(lt.get_supported_languages("es"))
# print(lt.get_supported_languages("all"))
# print(lt.get_supported_languages("auto"))
# print(lt.translate("Hola Mundo de la programación", "es", "en"))
