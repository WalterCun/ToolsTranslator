from pathlib import Path

import pytest

from translator.core.translator import Translator
from translator.exceptions import ExtraNotInstalledError, LanguageNotAvailableError, ServiceUnavailableError
from translator.file_handlers.json_handler import JsonHandler


class _FailClient:
    def translate(self, text: str, source: str, target: str) -> str:
        raise ServiceUnavailableError("down")


def test_translate_with_fallback_callable() -> None:
    t = Translator(directory="./tests/assets", lang="es")
    t.client = _FailClient()

    out = t.translate("hola", source="es", target="en", fallback=lambda txt: f"pending:{txt}")

    assert out == "pending:hola"


def test_missing_key_returns_key_when_auto_add_disabled(tmp_path: Path) -> None:
    t = Translator(directory=tmp_path, lang="es", auto_add_missing_keys=False)

    assert t.get("unknown.key") == "unknown.key"
    assert (tmp_path / "es.json").exists() is False


def test_auto_add_missing_keys_writes_nested_key(tmp_path: Path) -> None:
    t = Translator(directory=tmp_path, lang="es", auto_add_missing_keys=True)

    out = t.get("dashboard.title")

    assert out == "TODO: agregar traducción"
    data = JsonHandler.read(tmp_path / "es.json")
    assert data["dashboard"]["title"] == "TODO: agregar traducción"


def test_dynamic_attr_access_for_flat_and_nested(tmp_path: Path) -> None:
    file = tmp_path / "es.json"
    JsonHandler.write(file, {"hola": "mundo", "bienvenida": {"usuario": "Hola"}})

    t = Translator(directory=tmp_path, lang="es")

    assert str(t.hola) == "mundo"
    assert str(t.bienvenida.usuario) == "Hola"


def test_change_lang_reload_without_recreating_instance(tmp_path: Path) -> None:
    JsonHandler.write(tmp_path / "es.json", {"hola": "mundo"})
    JsonHandler.write(tmp_path / "en.json", {"hola": "world"})

    t = Translator(directory=tmp_path, lang="es")
    assert t.get("hola") == "mundo"

    t.lang = "en"
    assert t.get("hola") == "world"


def test_change_lang_raises_for_unknown_when_languages_exist(tmp_path: Path) -> None:
    JsonHandler.write(tmp_path / "es.json", {"hola": "mundo"})
    t = Translator(directory=tmp_path, lang="es")

    with pytest.raises(LanguageNotAvailableError):
        t.change_lang("fr")


def test_generate_language_file_keeps_text_on_fail(tmp_path: Path) -> None:
    source = tmp_path / "es.json"
    source.write_text('{"hello":"hola"}', encoding="utf-8")

    t = Translator(directory=tmp_path, lang="es")
    t.client = _FailClient()
    out = t.generate_language_file(source, "en", tmp_path / "en.json", source_lang="es")

    assert out["hello"] == "hola"


def test_yaml_methods_raise_without_extra(tmp_path: Path) -> None:
    t = Translator(directory=tmp_path)
    source = tmp_path / "es.json"
    source.write_text('{"hello":"hola"}', encoding="utf-8")

    try:
        import yaml  # type: ignore  # pragma: no cover
    except ImportError:
        with pytest.raises(ExtraNotInstalledError):
            t.convert_json_to_yaml(source, tmp_path / "es.yaml")
