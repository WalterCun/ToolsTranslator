from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Callable

from toolstranslator.adapters.libretranslate import LibreTranslateClient
from toolstranslator.config import settings
from toolstranslator.exceptions import LanguageNotAvailableError, TranslationFileError
from toolstranslator.file_handlers.json_handler import JsonHandler
from toolstranslator.file_handlers.yaml_handler import YamlHandler


class TranslationProxy:
    """Proxy for dynamic dotted access (`trans.home.title`)."""

    def __init__(self, translator: Translator, parts: list[str]) -> None:
        self._translator = translator
        self._parts = parts

    def __getattr__(self, item: str) -> TranslationProxy | str:
        return self._translator._resolve_attr(self._parts + [item])

    def __str__(self) -> str:
        return self._translator.get(".".join(self._parts))

    def __repr__(self) -> str:
        return str(self)


class Translator:
    """Public SDK entrypoint with proxy + file workflows and backward compatibility."""

    DEFAULT_MISSING_TEXT = "TODO: agregar traducción"

    def __init__(
        self,
        lang: str | None = None,
        directory: str | Path | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        missing_key_behavior: str | None = None,
        auto_add_missing_keys: bool = False,
        fallback_lang: str | None = None,
        missing_value_template: str = DEFAULT_MISSING_TEXT,
    ) -> None:
        self.directory = Path(directory) if directory else settings.locale_dir
        self.directory.mkdir(parents=True, exist_ok=True)
        self.log = logging.getLogger("toolstranslator")
        self.client = LibreTranslateClient(base_url=base_url or settings.base_url, timeout=timeout or settings.timeout)

        self._lang = lang or settings.default_target_lang
        self.fallback_lang = fallback_lang
        self._auto_add_missing_keys = auto_add_missing_keys
        self.missing_key_behavior = missing_key_behavior or settings.missing_key_behavior
        self.missing_value_template = missing_value_template

        self._file_lock = threading.RLock()
        self._lang_cache: dict[str, dict[str, Any]] = {}
        self._resolved_cache: dict[tuple[str, str], str] = {}
        self._current_data: dict[str, Any] = self._load_language(self._lang)

    @property
    def lang(self) -> str:
        return self._lang

    @lang.setter
    def lang(self, value: str) -> None:
        self.change_lang(value)

    @property
    def auto_add_missing_keys(self) -> bool:
        return self._auto_add_missing_keys

    @auto_add_missing_keys.setter
    def auto_add_missing_keys(self, value: bool) -> None:
        self._auto_add_missing_keys = bool(value)

    def change_lang(self, lang: str) -> None:
        self._current_data = self._load_language(lang)
        self._lang = lang

    def available_languages(self) -> list[str]:
        langs = sorted({p.stem for p in self.directory.glob("*.json")} | {p.stem for p in self.directory.glob("*.yaml")})
        return langs

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

    def get(
        self,
        key: str,
        lang: str | None = None,
        default: str | None = None,
        remote_target_lang: str | None = None,
    ) -> str:
        use_lang = lang or self._lang
        cache_key = (use_lang, key)
        if cache_key in self._resolved_cache and remote_target_lang is None:
            return self._resolved_cache[cache_key]

        data = self._load_language(use_lang)
        value = self._deep_get(data, key)
        if value is None:
            if self.auto_add_missing_keys and use_lang == self._lang:
                self._add_missing_key(key)
                value = self.missing_value_template
            else:
                value = self._missing_value(key, default)
        elif isinstance(value, dict):
            return str(TranslationProxy(self, key.split(".")))
        else:
            value = self._resolve_dynamic_value(value, use_lang, remote_target_lang)

        resolved = str(value)
        if remote_target_lang is None:
            self._resolved_cache[cache_key] = resolved
        return resolved

    def __getattr__(self, item: str) -> TranslationProxy | str:
        if item.startswith("_"):
            raise AttributeError(item)
        return self._resolve_attr([item])

    def _resolve_attr(self, parts: list[str]) -> TranslationProxy | str:
        key = ".".join(parts)
        data = self._current_data
        value = self._deep_get(data, key)
        if isinstance(value, dict) or value is None:
            return TranslationProxy(self, parts)
        return str(self._resolve_dynamic_value(value, self._lang, None))

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
        flat = self._flatten(data)
        translated: dict[str, str] = {}
        for key, value in flat.items():
            text = str(value)
            try:
                translated[key] = self.translate(text, source=source_lang, target=target_lang)
            except Exception as exc:
                self.log.error("Translation failed for key=%s: %s", key, exc)
                translated[key] = f"__PENDING__:{text}" if mark_pending else text

        nested_output = self._unflatten(translated)
        self._write_file(Path(output), nested_output)
        return translated

    def convert_json_to_yaml(self, json_file: str | Path, yaml_file: str | Path) -> None:
        data = JsonHandler.read(Path(json_file))
        YamlHandler.write(Path(yaml_file), data)

    def convert_yaml_to_json(self, yaml_file: str | Path, json_file: str | Path) -> None:
        data = YamlHandler.read(Path(yaml_file))
        JsonHandler.write(Path(json_file), data)

    def _resolve_dynamic_value(self, value: Any, source_lang: str, remote_target_lang: str | None) -> str:
        if isinstance(value, dict) and "__translate__" in value:
            text = str(value["__translate__"])
            source = str(value.get("source", source_lang))
            target = remote_target_lang or str(value.get("target", settings.default_target_lang))
            return self.translate(text, source=source, target=target, fallback=text)

        if isinstance(value, str) and value.startswith("__translate__:"):
            text = value.split(":", 1)[1]
            target = remote_target_lang or settings.default_target_lang
            return self.translate(text, source=source_lang, target=target, fallback=text)
        return str(value)

    def _load_language(self, lang: str) -> dict[str, Any]:
        if lang in self._lang_cache:
            return self._lang_cache[lang]

        data = self._read_lang_file(lang)
        if not data:
            if self.fallback_lang:
                fallback_data = self._read_lang_file(self.fallback_lang)
                if fallback_data:
                    self.log.warning("Language '%s' not found. Using fallback '%s'.", lang, self.fallback_lang)
                    self._lang_cache[lang] = fallback_data
                    return fallback_data
            if self.available_languages():
                raise LanguageNotAvailableError(
                    f"Language '{lang}' not found in {self.directory}. Available: {', '.join(self.available_languages())}"
                )

        self._lang_cache[lang] = data
        return data

    def _read_lang_file(self, lang: str) -> dict[str, Any]:
        json_path = self.directory / f"{lang}.json"
        if json_path.exists():
            return JsonHandler.read(json_path)

        yaml_path = self.directory / f"{lang}.yaml"
        if yaml_path.exists():
            return YamlHandler.read(yaml_path)

        yml_path = self.directory / f"{lang}.yml"
        if yml_path.exists():
            return YamlHandler.read(yml_path)

        return {}

    def _write_lang_file(self, lang: str, data: dict[str, Any]) -> None:
        json_path = self.directory / f"{lang}.json"
        yaml_path = self.directory / f"{lang}.yaml"
        yml_path = self.directory / f"{lang}.yml"

        if yaml_path.exists():
            YamlHandler.write(yaml_path, data)
            return
        if yml_path.exists():
            YamlHandler.write(yml_path, data)
            return
        JsonHandler.write(json_path, data)

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

    def _add_missing_key(self, key: str) -> None:
        with self._file_lock:
            current = self._read_lang_file(self._lang)
            if self._deep_get(current, key) is None:
                self._deep_set(current, key, self.missing_value_template)
                self._write_lang_file(self._lang, current)
                self._lang_cache[self._lang] = current
                self._current_data = current
            self._resolved_cache[(self._lang, key)] = self.missing_value_template

    @staticmethod
    def _deep_get(data: dict[str, Any], dotted_key: str) -> Any:
        current: Any = data
        for part in dotted_key.split("."):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current

    @staticmethod
    def _deep_set(data: dict[str, Any], dotted_key: str, value: Any) -> None:
        parts = dotted_key.split(".")
        current = data
        for part in parts[:-1]:
            node = current.get(part)
            if not isinstance(node, dict):
                node = {}
                current[part] = node
            current = node
        current[parts[-1]] = value

    @staticmethod
    def _flatten(data: dict[str, Any], parent: str = "") -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in data.items():
            full = f"{parent}.{key}" if parent else key
            if isinstance(value, dict) and "__translate__" not in value:
                out.update(Translator._flatten(value, full))
            else:
                out[full] = value
        return out

    @staticmethod
    def _unflatten(data: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in data.items():
            Translator._deep_set(out, key, value)
        return out
