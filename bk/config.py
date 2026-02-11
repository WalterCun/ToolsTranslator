# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" bk/config.py """

import logging
from pathlib import Path

from pydantic_settings import BaseSettings

from bk import __version__

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Represents the application settings used for configuration.

    Provides a structure for defining application settings with default values,
    ensuring easy maintainability and adherence to consistent defaults.

    """
    APP_NAME: str = "Tools Translator"
    APP_VERSION: str = __version__
    DEBUG: bool = True

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    HEADERS: dict[str, str] = {
        # "User-Agent": (
        #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        #     "Chrome/108.0.0.0 Safari/537.36"
        # ),
        # "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json"
    }

    class Config:
        """
        Handles application configuration and loading of environment variables.

        This class provides mechanisms to load configuration data required for the
        application, using environment variables from a specified `.env` file.
        It aims to centralize the configuration process, ensuring a structured
        approach to managing environment-specific settings.

        :ivar env_file: The path to the `.env` file containing environment variables.
        :type env_file: Str
        """
        env_file = str(Path(__file__).resolve().parent.parent / ".env")  # Ruta al archivo .env


# noinspection PyArgumentList
settings = Settings()
