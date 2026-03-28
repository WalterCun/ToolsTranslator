"""Tests for error handling — corrupt files, custom adapters, edge cases."""

import json
from pathlib import Path

import pytest

from translator import Translator, TranslationAdapter
from translator.exceptions import TranslationFileError
from translator.handlers.json_handler import JsonHandler
from translator.handlers.yaml_handler import YamlHandler


# --- Corrupt file tests ---

class TestCorruptJson:
    def test_corrupt_json_raises_translation_file_error(self, tmp_path: Path) -> None:
        """Corrupt JSON file should raise TranslationFileError, not JSONDecodeError."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        json_file = locale_dir / "en.json"
        json_file.write_text('{"hello": "wor', encoding="utf-8")  # incomplete JSON

        with pytest.raises(TranslationFileError, match="Invalid JSON"):
            JsonHandler.read(json_file)

    def test_corrupt_json_error_contains_path(self, tmp_path: Path) -> None:
        """Error message should include the file path for debugging."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        json_file = locale_dir / "bad.json"
        json_file.write_text("{invalid}", encoding="utf-8")

        with pytest.raises(TranslationFileError, match=str(json_file)):
            JsonHandler.read(json_file)

    def test_empty_json_file(self, tmp_path: Path) -> None:
        """Empty JSON file should raise TranslationFileError."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        json_file = locale_dir / "empty.json"
        json_file.write_text("", encoding="utf-8")

        with pytest.raises(TranslationFileError):
            JsonHandler.read(json_file)


class TestCorruptYaml:
    def test_corrupt_yaml_raises_translation_file_error(self, tmp_path: Path) -> None:
        """Corrupt YAML file should raise TranslationFileError."""
        pytest.importorskip("yaml")
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        yaml_file = locale_dir / "en.yaml"
        yaml_file.write_text("hello: \n  - bad\n  indent\n", encoding="utf-8")

        with pytest.raises(TranslationFileError, match="Invalid YAML"):
            YamlHandler.read(yaml_file)


class TestMissingLanguageFile:
    def test_missing_language_uses_fallback(self, tmp_path: Path) -> None:
        """When requested language doesn't exist, fallback should be used."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text('{"hello": "Hello"}', encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir, fallback_lang="en")
        t.change_lang("fr")  # fr.json doesn't exist, should fall back to en
        assert t.get("hello") == "Hello"


# --- Custom adapter tests ---

class FakeAdapter:
    """Minimal adapter for testing."""

    def __init__(self, translations: dict[str, str] | None = None) -> None:
        self._translations = translations or {}
        self._call_count = 0

    def available(self) -> tuple[bool, str]:
        return True, "fake"

    def translate(self, text: str, source: str, target: str) -> str:
        self._call_count += 1
        return self._translations.get(text, f"[{target}] {text}")


class TestCustomAdapter:
    def test_custom_adapter_is_used(self, tmp_path: Path) -> None:
        """Translator should use the injected adapter instead of creating LibreTranslate."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text('{}', encoding="utf-8")

        adapter = FakeAdapter({"hello": "hola"})
        t = Translator(lang="en", directory=locale_dir, adapter=adapter)

        result = t.translate("hello")
        assert result == "hola"
        assert adapter._call_count == 1

    def test_default_adapter_without_param(self, tmp_path: Path) -> None:
        """Without adapter param, Translator creates LibreTranslateClient."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text('{}', encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir)
        from translator.adapters.libretranslate import LibreTranslateClient
        assert isinstance(t.client, LibreTranslateClient)

    def test_adapter_protocol_check(self) -> None:
        """FakeAdapter should satisfy TranslationAdapter protocol."""
        adapter = FakeAdapter()
        assert isinstance(adapter, TranslationAdapter)

    def test_translate_with_fallback(self, tmp_path: Path) -> None:
        """translate() should use fallback when adapter raises."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text('{}', encoding="utf-8")

        class FailingAdapter:
            def available(self) -> tuple[bool, str]:
                return True, "ok"

            def translate(self, text: str, source: str, target: str) -> str:
                raise RuntimeError("server down")

        t = Translator(lang="en", directory=locale_dir, adapter=FailingAdapter())
        result = t.translate("hello", fallback="fallback_text")
        assert result == "fallback_text"

    def test_translate_callable_fallback(self, tmp_path: Path) -> None:
        """translate() should call fallback function when adapter raises."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text('{}', encoding="utf-8")

        class FailingAdapter:
            def available(self) -> tuple[bool, str]:
                return True, "ok"

            def translate(self, text: str, source: str, target: str) -> str:
                raise RuntimeError("server down")

        t = Translator(lang="en", directory=locale_dir, adapter=FailingAdapter())
        result = t.translate("hello", fallback=lambda t: f"fallback: {t}")
        assert result == "fallback: hello"
