#!/usr/bin/env python3
""" translate_api.py """
import logging
import time
from datetime import timedelta
from pprint import pprint

import requests
import requests_cache

from translator.config import settings

log = logging.getLogger(__name__)

# Configuración de la caché usando SQLite (persistente)
requests_cache.install_cache(
    "translate_cache",  # Nombre de la base de datos SQLite para la caché
    expire_after=timedelta(minutes=60 * 24)  # Tiempo de expiración de los datos en caché
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
        self.url_translate = url + 'translate'
        self.url_languages = url + 'languages'
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _request_supported_languages(self):
        """
        Méto.do que realiza la solicitud HTTP para obtener los idiomas soportados.
        """
        log.info("Solicitando lista de idiomas soportados...")
        try:
            response = requests.get(self.url_languages, headers=settings.HEADERS)
            response.raise_for_status()  # Lanza un error si el código HTTP indica un fallo.
            return response.json()
        except requests.RequestException as e:
            requests_cache.clear()
            raise Exception(f"Error al realizar la solicitud: {str(e)}")

    def get_supported_languages(self, lang_base):
        """
        Requests the list of supported languages from the API and stores it in a cache.

        :param retry: int
            The current retry attempt count, used for managing retries on failure.

        :return: list[dict]
            A list of dictionaries containing language information. Returns an empty list if an error occurs.
        """
        try:
            response = self._request_supported_languages()
            languages = set()
            if response:
                for i in response:
                    if lang_base == i.get('code'):
                        return i.get('targets') or []
                    elif lang_base == 'auto':
                        languages.add(i.get('code'))
            return list(languages) or []
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

        while retry <= self.max_retries:
            try:
                with requests_cache.disabled():
                    response = requests.post(self.url_translate, json=payload, headers=settings.HEADERS,
                                             timeout=self.retry_delay or 3)
                    if response.status_code == 200:
                        translated_text = response.json().get("translatedText", "")
                        if not translated_text:
                            log.error("La respuesta del servidor no contiene la traducción.")
                        return translated_text
                    else:
                        log.error(f"Error: {response.status_code}, {response.content}")
            except requests.RequestException as e:
                log.error(f"Excepción en la traducción: {str(e)}")
            retry += 1

        return ""
