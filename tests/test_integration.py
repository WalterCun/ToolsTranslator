"""Integration tests — full workflows with mock adapters."""

import json
from pathlib import Path

import pytest

from translator import Translator, TranslationAdapter
from translator.handlers.json_handler import JsonHandler
from translator.handlers.io_handlers import read_mapping, write_mapping


class MockAdapter:
    """Adapter that translates by wrapping text with target language."""

    def __init__(self) -> None:
        self.call_count = 0

    def available(self) -> tuple[bool, str]:
        return True, "ok"

    def translate(self, text: str, source: str, target: str) -> str:
        self.call_count += 1
        return f"[{target}] {text}"


class TestGenerateLanguageFile:
    def test_generates_translated_file(self, tmp_path: Path) -> None:
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        base_file = locale_dir / "en.json"
        base_file.write_text(json.dumps({
            "greeting": "Hello",
            "farewell": "Goodbye",
            "nested": {"key": "value"},
        }), encoding="utf-8")

        adapter = MockAdapter()
        t = Translator(lang="en", directory=locale_dir, adapter=adapter)
        output = locale_dir / "es.json"

        result = t.generate_language_file(base_file, "es", output)

        assert output.exists()
        assert result["greeting"] == "[es] Hello"
        assert result["farewell"] == "[es] Goodbye"
        assert result["nested.key"] == "[es] value"

        # Verify written file
        content = json.loads(output.read_text())
        assert content["greeting"] == "[es] Hello"
        assert content["nested"]["key"] == "[es] value"

    def test_pending_mark_on_failure(self, tmp_path: Path) -> None:
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        base_file = locale_dir / "en.json"
        base_file.write_text('{"key": "value"}', encoding="utf-8")

        class FailingAdapter:
            def available(self) -> tuple[bool, str]:
                return True, "ok"
            def translate(self, text, source, target):
                raise RuntimeError("fail")

        t = Translator(lang="en", directory=locale_dir, adapter=FailingAdapter())
        output = locale_dir / "es.json"
        result = t.generate_language_file(base_file, "es", output, mark_pending=True)

        assert result["key"] == "__PENDING__:value"


class TestFormatConversion:
    def test_json_to_yaml(self, tmp_path: Path) -> None:
        pytest.importorskip("yaml")
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        json_file = locale_dir / "en.json"
        yaml_file = locale_dir / "en.yaml"
        json_file.write_text(json.dumps({"key": "value", "nested": {"a": 1}}), encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir)
        t.convert_json_to_yaml(json_file, yaml_file)

        assert yaml_file.exists()
        content = read_mapping(yaml_file)
        assert content["key"] == "value"
        assert content["nested"]["a"] == 1

    def test_yaml_to_json(self, tmp_path: Path) -> None:
        pytest.importorskip("yaml")
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        yaml_file = locale_dir / "en.yaml"
        json_file = locale_dir / "en.json"

        from translator.handlers.yaml_handler import YamlHandler
        YamlHandler.write(yaml_file, {"key": "value"})

        t = Translator(lang="en", directory=locale_dir)
        t.convert_yaml_to_json(yaml_file, json_file)

        assert json_file.exists()
        content = json.loads(json_file.read_text())
        assert content["key"] == "value"


class TestEndToEndWorkflow:
    """Full workflow: init -> read -> switch lang -> add missing -> convert."""

    def test_complete_workflow(self, tmp_path: Path) -> None:
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()

        # 1. Create initial locale files
        en_data = {
            "app": {
                "title": "My App",
                "buttons": {"save": "Save", "cancel": "Cancel"},
            },
            "greeting": "Hello",
        }
        es_data = {
            "app": {
                "title": "Mi App",
                "buttons": {"save": "Guardar"},
            },
        }
        (locale_dir / "en.json").write_text(json.dumps(en_data), encoding="utf-8")
        (locale_dir / "es.json").write_text(json.dumps(es_data), encoding="utf-8")

        # 2. Init translator with English
        t = Translator(lang="en", directory=locale_dir, adapter=MockAdapter())
        assert t.app.title == "My App"
        assert t.app.buttons.save == "Save"
        assert t.greeting == "Hello"

        # 3. Switch to Spanish
        t.change_lang("es")
        assert t.app.title == "Mi App"
        assert t.app.buttons.save == "Guardar"

        # 4. Check available languages
        langs = t.available_languages()
        assert "en" in langs
        assert "es" in langs

        # 5. Switch back to English
        t.lang = "en"
        assert t.greeting == "Hello"

        # 6. Use get() with dot notation
        assert t.get("app.buttons.save") == "Save"
        assert t.get("app.buttons.cancel") == "Cancel"

        # 7. Test missing key with default
        assert t.get("nonexistent", default="fallback") == "fallback"

        # 8. Test with adapter translation
        result = t.translate("hello world")
        assert result == "[en] hello world"

    def test_protocol_is_runtime_checkable(self) -> None:
        """TranslationAdapter should work with isinstance at runtime."""
        adapter = MockAdapter()
        assert isinstance(adapter, TranslationAdapter)

    def test_adapter_protocol_rejects_bad_objects(self) -> None:
        """Objects missing required methods should not pass protocol check."""
        class BadAdapter:
            def available(self):
                return True, "ok"
            # missing translate()

        bad = BadAdapter()
        assert not isinstance(bad, TranslationAdapter)
