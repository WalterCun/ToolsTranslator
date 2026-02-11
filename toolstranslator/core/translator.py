from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

from toolstranslator.adapters.libretranslate import LibreTranslateClient
from toolstranslator.config import settings
from toolstranslator.exceptions import TranslationFileError
from toolstranslator.file_handlers.json_handler import JsonHandler
from toolstranslator.file_handlers.yaml_handler import YamlHandler


class Translator:
    """Public SDK entrypoint with proxy + file workflows."""

    def __init__(
        self,
        directory: str | Path | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        missing_key_behavior: str | None = None,
    ) -> None:
        self.directory = Path(directory) if directory else settings.locale_dir
        self.directory.mkdir(parents=True, exist_ok=True)
        self.missing_key_behavior = missing_key_behavior or settings.missing_key_behavior
        self.log = logging.getLogger("toolstranslator")
        self.client = LibreTranslateClient(
            base_url=base_url or settings.base_url,
            timeout=timeout or settings.timeout,
        )

    def translate(
        self,
        text: str,
        source: str | None = None,
        target: str | None = None,
        fallback: Callable[[str], str] | str | None = None,
    ) -> str:
        source_lang = source or settings.default_source_lang
        target_lang = target or settings.default_target_lang
        try:
            return self.client.translate(text=text, source=source_lang, target=target_lang)
        except Exception:
            if callable(fallback):
                return fallback(text)
            if isinstance(fallback, str):
                return fallback
            raise

    async def translate_async(self, text: str, source: str | None = None, target: str | None = None) -> str:
        source_lang = source or settings.default_source_lang
        target_lang = target or settings.default_target_lang
        return await self.client.translate_async(text=text, source=source_lang, target=target_lang)

    def get(self, key: str, lang: str, default: str | None = None) -> str:
        data = self._read_lang_file(lang)
        if key in data:
            return str(data[key])
        return self._missing_value(key, default)

    def generate_language_file(
        self,
        base_file: str | Path,
        target_lang: str,
        output: str | Path,
        source_lang: str | None = None,
        mark_pending: bool = False,
    ) -> dict[str, str]:
        base_path = Path(base_file)
        if not base_path.exists():
            raise TranslationFileError(f"Base file not found: {base_path}")

        data = self._read_file(base_path)
        translated: dict[str, str] = {}
        for key, value in data.items():
            text = str(value)
            try:
                translated[key] = self.translate(text, source=source_lang, target=target_lang)
            except Exception as exc:
                self.log.error("Translation failed for key=%s: %s", key, exc)
                translated[key] = f"__PENDING__:{text}" if mark_pending else text

        self._write_file(Path(output), translated)
        return translated

    def convert_json_to_yaml(self, json_file: str | Path, yaml_file: str | Path) -> None:
        data = JsonHandler.read(Path(json_file))
        YamlHandler.write(Path(yaml_file), data)

    def convert_yaml_to_json(self, yaml_file: str | Path, json_file: str | Path) -> None:
        data = YamlHandler.read(Path(yaml_file))
        JsonHandler.write(Path(json_file), data)

    def _read_lang_file(self, lang: str) -> dict[str, Any]:
        json_path = self.directory / f"{lang}.json"
        if json_path.exists():
            return JsonHandler.read(json_path)

        yaml_path = self.directory / f"{lang}.yaml"
        if yaml_path.exists():
            return YamlHandler.read(yaml_path)

        return {}

    def _read_file(self, path: Path) -> dict[str, Any]:
        if path.suffix.lower() == ".json":
            return JsonHandler.read(path)
        if path.suffix.lower() in {".yaml", ".yml"}:
            return YamlHandler.read(path)
        raise TranslationFileError(f"Unsupported file format: {path.suffix}")

    def _write_file(self, path: Path, data: dict[str, Any]) -> None:
        if path.suffix.lower() == ".json":
            JsonHandler.write(path, data)
            return
        if path.suffix.lower() in {".yaml", ".yml"}:
            YamlHandler.write(path, data)
            return
        raise TranslationFileError(f"Unsupported output format: {path.suffix}")

    def _missing_value(self, key: str, default: str | None) -> str:
        if default is not None:
            return default
        if self.missing_key_behavior == "message":
            return "Missing translation"
        return key
