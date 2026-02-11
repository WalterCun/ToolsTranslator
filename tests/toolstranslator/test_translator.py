from pathlib import Path

import pytest

from toolstranslator.core.translator import Translator
from toolstranslator.exceptions import ExtraNotInstalledError, ServiceUnavailableError


class _OkClient:
    def translate(self, text: str, source: str, target: str) -> str:
        return f"{text}:{source}->{target}"


class _FailClient:
    def translate(self, text: str, source: str, target: str) -> str:
        raise ServiceUnavailableError("down")


def test_translate_with_fallback_callable() -> None:
    t = Translator(directory="./tests/assets")
    t.client = _FailClient()

    out = t.translate("hola", source="es", target="en", fallback=lambda txt: f"pending:{txt}")

    assert out == "pending:hola"


def test_missing_key_returns_key(tmp_path: Path) -> None:
    t = Translator(directory=tmp_path)
    assert t.get("unknown.key", lang="es") == "unknown.key"


def test_generate_language_file_keeps_text_on_fail(tmp_path: Path) -> None:
    source = tmp_path / "es.json"
    source.write_text('{"hello":"hola"}', encoding="utf-8")

    t = Translator(directory=tmp_path)
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
