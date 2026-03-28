"""Tests for TranslateFile — language detection from filenames."""

from pathlib import Path

import pytest

from translator.utils.fileinfo import TranslateFile


class TestDetectLangFromName:
    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("es.json", "es"),
            ("en.json", "en"),
            ("pt_BR.json", "pt_BR"),
            ("zh_Hans.yaml", "zh_Hans"),
            ("messages.es.json", "es"),
            ("app.en.yml", "en"),
            ("translations.pt_BR.json", "pt_BR"),
        ],
    )
    def test_valid_language_codes(self, filename: str, expected: str) -> None:
        tf = TranslateFile(path=Path(filename))
        assert tf.detect_lang_from_name() == expected

    @pytest.mark.parametrize(
        "filename",
        [
            "hello.json",       # 5 chars but not a language code
            "world.yaml",       # 5 chars but not a language code
            "translations.json",  # no language code
            "README.md",
            "config.json",      # 6 chars
        ],
    )
    def test_invalid_language_codes(self, filename: str) -> None:
        """Should return None for filenames that don't contain valid language codes."""
        tf = TranslateFile(path=Path(filename))
        assert tf.detect_lang_from_name() is None

    def test_properties(self) -> None:
        tf = TranslateFile(path=Path("/locales/es.json"))
        assert tf.stem == "es"
        assert tf.extension == ".json"
        assert tf.filename == "es.json"
        assert tf.directory == Path("/locales")
