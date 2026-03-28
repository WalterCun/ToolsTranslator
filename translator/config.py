from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    """Runtime configuration loaded from env vars with safe defaults."""

    base_url: str = os.getenv("TOOLSTRANSLATOR_BASE_URL", "http://localhost:5000")
    timeout: float = float(os.getenv("TOOLSTRANSLATOR_TIMEOUT", "10"))
    default_source_lang: str = os.getenv("TOOLSTRANSLATOR_SOURCE_LANG", "auto")
    default_target_lang: str = os.getenv("TOOLSTRANSLATOR_TARGET_LANG", "en")
    locale_dir: Path = Path(os.getenv("TOOLSTRANSLATOR_LOCALE_DIR", "./locales"))
    missing_key_behavior: str = os.getenv("TOOLSTRANSLATOR_MISSING_KEY", "key")
    log_level: str = os.getenv("TOOLSTRANSLATOR_LOG_LEVEL", "INFO")


settings = Settings()


def _configure_logging() -> None:
    """Configure the 'translator' logger based on settings.log_level."""
    logger = logging.getLogger("translator")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(name)s %(levelname)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))


_configure_logging()
