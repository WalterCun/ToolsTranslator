from __future__ import annotations

import logging
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any, Callable

from translator.adapters.base import TranslationAdapter
from translator.adapters.libretranslate import LibreTranslateClient
from translator.config import settings
from translator.exceptions import LanguageNotAvailableError, TranslationFileError
from translator.handlers.io_handlers import flatten, read_mapping, unflatten, write_mapping
from translator.handlers.json_handler import JsonHandler
from translator.handlers.yaml_handler import YamlHandler


class _LRUCache:
    """Bounded LRU cache using OrderedDict. Evicts oldest entries when exceeding max_size."""

    def __init__(self, max_size: int = 50) -> None:
        self._max_size = max_size
        self._data: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __getitem__(self, key: str) -> dict[str, Any]:
        self._data.move_to_end(key)
        return self._data[key]

    def __setitem__(self, key: str, value: dict[str, Any]) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        while len(self._data) > self._max_size:
            self._data.popitem(last=False)

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def clear(self) -> None:
        self._data.clear()


class TranslationProxy:
    """Proxy for dynamic dotted access (`trans.home.title`)."""

    def __init__(self, translator: Translator, parts: list[str]) -> None:
        self._translator = translator
        self._parts = parts

    def __getattr__(self, item: str) -> TranslationProxy | str:
        return self._translator._resolve_attr(self._parts + [item])

    def __str__(self) -> str:
        key = ".".join(self._parts)
        data = self._translator._current_data
        value = self._translator._deep_get(data, key)
        if isinstance(value, dict):
            # Return the key itself for dict nodes (avoids recursion)
            return key
        if value is not None:
            return str(self._translator._resolve_dynamic_value(value, self._translator._lang, None))
        return key

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
        adapter: TranslationAdapter | None = None,
    ) -> None:
        self.directory = Path(directory) if directory else settings.locale_dir
        self.directory.mkdir(parents=True, exist_ok=True)
        self.log = logging.getLogger("translator")

        if adapter is not None:
            self.client: TranslationAdapter = adapter
        else:
            self.client = LibreTranslateClient(
                base_url=base_url or settings.base_url,
                timeout=timeout or settings.timeout,
            )

        self._lang = lang or settings.default_target_lang
        # fallback_lang: None = auto (defaults to lang), "" = disabled, "xx" = explicit
        if fallback_lang is None:
            self.fallback_lang: str = self._lang
        else:
            self.fallback_lang = fallback_lang
        self._auto_add_missing_keys = auto_add_missing_keys
        self.missing_key_behavior = missing_key_behavior or settings.missing_key_behavior
        self.missing_value_template = missing_value_template

        self._file_lock = threading.RLock()
        self._lang_cache: _LRUCache = _LRUCache(max_size=50)
        self._resolved_cache: dict[tuple[str, str], str] = {}
        self._available_cache: list[str] | None = None
        self._current_data: dict[str, Any] = self._load_language(self._lang)
        self._metrics: dict[str, int] = {
            "get_calls": 0,
            "translate_calls": 0,
            "cache_hits": 0,
            "missing_keys": 0,
        }

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

    @property
    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)

    def __contains__(self, key: str) -> bool:
        """Check if a translation key exists."""
        return self._deep_get(self._current_data, key) is not None

    def __iter__(self):
        """Iterate over all translation keys (dotted notation)."""
        return iter(self._flatten(self._current_data).keys())

    def __len__(self) -> int:
        """Count of translation keys."""
        return len(self._flatten(self._current_data))

    def change_lang(self, lang: str) -> None:
        self._current_data = self._load_language(lang)
        old_lang = self._lang
        self._lang = lang
        self._resolved_cache.clear()
        self.log.debug("Language changed: %s -> %s", old_lang, lang)

    def available_languages(self) -> list[str]:
        if self._available_cache is not None:
            return self._available_cache
        langs = sorted({p.stem for p in self.directory.glob("*.json")} | {p.stem for p in self.directory.glob("*.yaml")} | {p.stem for p in self.directory.glob("*.yml")})
        self._available_cache = langs
        return langs

    def _resolve_langs(self, source: str | None, target: str | None) -> tuple[str, str]:
        """Resolve source and target languages with defaults."""
        return (
            source or settings.default_source_lang,
            target or settings.default_target_lang,
        )

    def translate(
        self,
        text: str,
        source: str | None = None,
        target: str | None = None,
        fallback: Callable[[str], str] | str | None = None,
    ) -> str:
        self._metrics["translate_calls"] += 1
        source_lang, target_lang = self._resolve_langs(source, target)
        try:
            return self.client.translate(text=text, source=source_lang, target=target_lang)
        except Exception:
            if callable(fallback):
                return fallback(text)
            if isinstance(fallback, str):
                return fallback
            raise

    async def translate_async(self, text: str, source: str | None = None, target: str | None = None) -> str:
        source_lang, target_lang = self._resolve_langs(source, target)
        return await self.client.translate_async(text=text, source=source_lang, target=target_lang)

    def get(
        self,
        key: str,
        lang: str | None = None,
        default: str | None = None,
        remote_target_lang: str | None = None,
    ) -> str:
        self._metrics["get_calls"] += 1
        use_lang = lang or self._lang
        cache_key = (use_lang, key)
        if cache_key in self._resolved_cache and remote_target_lang is None:
            self._metrics["cache_hits"] += 1
            return self._resolved_cache[cache_key]

        data = self._load_language(use_lang)
        value = self._deep_get(data, key)
        if value is None:
            self._metrics["missing_keys"] += 1
            if self.auto_add_missing_keys and use_lang == self._lang:
                self._add_missing_key(key)
                value = self.missing_value_template
            else:
                value = self._missing_value(key, default)
        elif isinstance(value, dict):
            # Dynamic translation blocks should be resolved, not navigated
            if "__translate__" in value:
                value = self._resolve_dynamic_value(value, use_lang, remote_target_lang)
            else:
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
        # Check resolved cache first for leaf values
        cache_key = (self._lang, key)
        if cache_key in self._resolved_cache:
            return self._resolved_cache[cache_key]

        data = self._current_data
        value = self._deep_get(data, key)
        if isinstance(value, dict) or value is None:
            return TranslationProxy(self, parts)

        resolved = str(self._resolve_dynamic_value(value, self._lang, None))
        self._resolved_cache[cache_key] = resolved
        return resolved

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
        if data is None:
            if self.fallback_lang:
                fallback_data = self._read_lang_file(self.fallback_lang)
                if fallback_data is not None:
                    self.log.warning("Language '%s' not found. Using fallback '%s'.", lang, self.fallback_lang)
                    self._lang_cache[lang] = fallback_data
                    return fallback_data
            if self.available_languages():
                raise LanguageNotAvailableError(
                    f"Language '{lang}' not found in {self.directory}. Available: {', '.join(self.available_languages())}"
                )
            return {}

        self._lang_cache[lang] = data
        return data

    def _read_lang_file(self, lang: str) -> dict[str, Any] | None:
        extensions = {".json": JsonHandler.read, ".yaml": YamlHandler.read, ".yml": YamlHandler.read}
        for ext, handler in extensions.items():
            path = self.directory / f"{lang}{ext}"
            if path.exists():
                return handler(path)
        return None

    def _write_lang_file(self, lang: str, data: dict[str, Any]) -> None:
        self._available_cache = None
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
        return read_mapping(path)

    def _write_file(self, path: Path, data: dict[str, Any]) -> None:
        write_mapping(path, data)

    def _missing_value(self, key: str, default: str | None) -> str:
        if default is not None:
            return default
        if self.missing_key_behavior == "message":
            return "Missing translation"
        self.log.debug("Missing translation key: %s (lang=%s)", key, self._lang)
        return key

    def _add_missing_key(self, key: str) -> None:
        with self._file_lock:
            self._available_cache = None
            current = self._read_lang_file(self._lang)
            if self._deep_get(current, key) is None:
                self._deep_set(current, key, self.missing_value_template)
                self._write_lang_file(self._lang, current)
                self._lang_cache[self._lang] = current
                self._current_data = current
                self.log.info("Auto-added missing key '%s' to %s.json", key, self._lang)
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
        """Flatten nested dict, preserving dynamic __translate__ blocks."""
        return flatten(data, parent, preserve_dynamic=True)

    @staticmethod
    def _unflatten(data: dict[str, Any]) -> dict[str, Any]:
        """Unflatten dotted keys back to nested dict."""
        return unflatten(data)
