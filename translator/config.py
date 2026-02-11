from __future__ import annotations

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
