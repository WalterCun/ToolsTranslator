#!/usr/bin/env python3
""" translate_api.py """
import logging
from functools import lru_cache

import requests

from translator.config import settings

log = logging.getLogger(__name__)


class LibreTranslate:
    """
    Represents a client for interacting with LibreTranslate API.

    This class provides functionality to translate text from one language to another
    using the LibreTranslate API. It also supports fetching available languages for
    translation. It handles retries, timeouts, and error logging for robust usage.

    :ivar url_translate: The URL endpoint for the translation functionality.
    :type url_translate: str
    :ivar url_languajes: The URL endpoint for fetching available languages.
    :type url_languajes: str
    :ivar max_retries: The maximum number of retry attempts for API calls.
    :type max_retries: int
    :ivar retry_delay: Delay (in seconds) between retry attempts.
    :type retry_delay: int
    """

    def __init__(self, url: str = "http://localhost:5000/", max_retries=3, retry_delay=3):
        self.url_translate = url + 'translate'
        self.url_languajes = url + 'languages'
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._languages_cache = None

    @lru_cache(maxsize=10)
    def get_supported_languages(self, retry=0):
        """
        Requests the list of supported languages from the API and stores it in a cache.

        :param retry: int
            The current retry attempt count, used for managing retries on failure.

        :return: list[dict]
            A list of dictionaries containing language information. Returns an empty list if an error occurs.
        """
        if self._languages_cache is not None:
            return self._languages_cache

        try:
            response = requests.get(self.url_languajes, headers=settings.HEADERS, timeout=self.retry_delay or 3)
            if response.status_code == 200:
                self._languages_cache = response.json()
                return self._languages_cache
            else:
                log.error(f"Error fetching languages: {response.status_code}, {response.content}")
        except requests.exceptions.RequestException as e:
            log.error(f"Request exception: {e}")

        if retry < self.max_retries:
            return self.get_supported_languages(retry + 1)

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

            response = requests.post(self.url_translate, json=payload, headers=settings.HEADERS, timeout=self.retry_delay or 3)

            if response.status_code != 200:
                log.error(f"Error: {response.status_code}, {response.content}")
                if retry <= self.max_retries:
                    return self.translate(text, source, target, retry + 1)
                return ""

            translated_text = response.json().get("translatedText", "")
            return translated_text


if __name__ == '__main__':
    libre = LibreTranslate()
    # print(libre.translate("Hola", "es", "en"))
    print(libre.get_supported_languages())
