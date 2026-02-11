from pathlib import Path

from translate import AutoTranslate, AutoTranslateOptions, TranslateFile
from translate.exceptions import ServerDependencyMissingError


class _FakeAdapter:
    def available(self):
        return True, "ok"

    def translate(self, text: str, source: str, target: str) -> str:
        return f"{text}:{source}->{target}"


def test_autotranslate_generates_nested_file(tmp_path: Path) -> None:
    base = tmp_path / "es.json"
    base.write_text('{"home":{"title":"Hola"}}', encoding="utf-8")

    tf = TranslateFile(base)
    args = AutoTranslateOptions(langs=["en"], nested=True)
    result = AutoTranslate(tf, args=args, adapter=_FakeAdapter()).worker()

    out = tmp_path / "en.json"
    assert out.exists()
    assert result.translated_keys == 1


def test_autotranslate_requires_adapter_without_server(tmp_path: Path) -> None:
    base = tmp_path / "es.json"
    base.write_text('{"hello":"hola"}', encoding="utf-8")

    tf = TranslateFile(base)
    args = AutoTranslateOptions(langs=["en"], nested=False)

    code, message = AutoTranslate.cli_worker(tf, args=args, use_server=False, adapter=None)

    assert code == 2
    assert "requires server support" in message


def test_detects_base_from_filename(tmp_path: Path) -> None:
    base = tmp_path / "es.json"
    base.write_text('{"hello":"hola"}', encoding="utf-8")

    tf = TranslateFile(base)
    args = AutoTranslateOptions(langs=["en"])
    result = AutoTranslate(tf, args=args, adapter=_FakeAdapter()).worker()

    assert result.total_keys == 1
