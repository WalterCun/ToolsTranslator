"""Integration tests for caching behavior and dynamic translation values."""

import json
from pathlib import Path

import pytest

from translator import Translator
from translator.handlers.json_handler import JsonHandler


# --- Resolved cache ---

class TestResolvedCache:
    def test_repeated_get_returns_cached(self, tmp_path: Path) -> None:
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text('{"key": "value"}', encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir)
        result1 = t.get("key")
        result2 = t.get("key")
        assert result1 == result2 == "value"

    def test_cache_invalidated_on_file_change(self, tmp_path: Path) -> None:
        """When auto_add_missing_keys writes to file, cache should update."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        json_file = locale_dir / "en.json"
        json_file.write_text('{"existing": "value"}', encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir, auto_add_missing_keys=True)
        # Access missing key — triggers file write
        val = t.get("new_key")
        assert val == "TODO: agregar traducción"
        # Verify file was updated
        content = json.loads(json_file.read_text())
        assert "new_key" in content


# --- Dynamic values ---

class TestDynamicValues:
    def test_translate_in_value_dict(self, tmp_path: Path) -> None:
        """__translate__ dict should trigger translation."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        data = {"greeting": {"__translate__": "Hello", "source": "en", "target": "es"}}
        (locale_dir / "en.json").write_text(json.dumps(data), encoding="utf-8")

        # Use a mock adapter that just returns the target prefixed text
        class MockAdapter:
            def available(self):
                return True, "ok"
            def translate(self, text, source, target):
                return f"[{target}] {text}"

        t = Translator(lang="en", directory=locale_dir, adapter=MockAdapter())
        result = t.get("greeting")
        assert result == "[es] Hello"

    def test_translate_in_value_string(self, tmp_path: Path) -> None:
        """__translate__: prefix should trigger translation."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        data = {"greeting": "__translate__:Hello"}
        (locale_dir / "en.json").write_text(json.dumps(data), encoding="utf-8")

        class MockAdapter:
            def available(self):
                return True, "ok"
            def translate(self, text, source, target):
                return f"[{target}] {text}"

        t = Translator(lang="en", directory=locale_dir, adapter=MockAdapter())
        result = t.get("greeting")
        assert result == "[en] Hello"  # default_target_lang is "en"

    def test_dynamic_value_fallback_on_error(self, tmp_path: Path) -> None:
        """When translation fails, should return original text."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        data = {"greeting": {"__translate__": "Hello"}}
        (locale_dir / "en.json").write_text(json.dumps(data), encoding="utf-8")

        class FailingAdapter:
            def available(self):
                return True, "ok"
            def translate(self, text, source, target):
                raise RuntimeError("fail")

        t = Translator(lang="en", directory=locale_dir, adapter=FailingAdapter())
        result = t.get("greeting")
        assert result == "Hello"  # fallback to original


# --- available_languages ---

class TestAvailableLanguages:
    def test_lists_json_languages(self, tmp_path: Path) -> None:
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text("{}", encoding="utf-8")
        (locale_dir / "es.json").write_text("{}", encoding="utf-8")
        (locale_dir / "fr.json").write_text("{}", encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir)
        langs = t.available_languages()
        assert langs == ["en", "es", "fr"]

    def test_lists_yaml_languages(self, tmp_path: Path) -> None:
        pytest.importorskip("yaml")
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text("{}", encoding="utf-8")
        (locale_dir / "es.yaml").write_text("{}", encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir)
        langs = t.available_languages()
        assert "en" in langs
        assert "es" in langs


# --- Fallback language ---

class TestFallbackLanguage:
    def test_fallback_used_when_lang_missing(self, tmp_path: Path) -> None:
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text('{"hello": "Hello"}', encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir, fallback_lang="en")
        t.change_lang("fr")  # fr doesn't exist, fallback to en
        assert t.get("hello") == "Hello"

    def test_fallback_lang_defaults_to_lang(self, tmp_path: Path) -> None:
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text('{"key": "val"}', encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir)
        assert t.fallback_lang == "en"
