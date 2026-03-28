"""Unit tests for io_handlers — flatten, unflatten, read_mapping, write_mapping."""

import json
from pathlib import Path

import pytest

from translator.exceptions import TranslationFileError
from translator.handlers.io_handlers import flatten, unflatten, read_mapping, write_mapping


# --- flatten ---

class TestFlatten:
    def test_simple_dict(self) -> None:
        data = {"a": 1, "b": 2}
        assert flatten(data) == {"a": 1, "b": 2}

    def test_nested_dict(self) -> None:
        data = {"home": {"title": "Bienvenido", "button": "Entrar"}}
        result = flatten(data)
        assert result == {"home.title": "Bienvenido", "home.button": "Entrar"}

    def test_deeply_nested(self) -> None:
        data = {"a": {"b": {"c": "value"}}}
        assert flatten(data) == {"a.b.c": "value"}

    def test_mixed_types(self) -> None:
        data = {"str": "hello", "num": 42, "bool": True, "none": None}
        result = flatten(data)
        assert result == {"str": "hello", "num": 42, "bool": True, "none": None}

    def test_preserve_dynamic_keeps_translate_blocks(self) -> None:
        data = {
            "static": "value",
            "dynamic": {"__translate__": "Hello", "source": "en"},
        }
        result = flatten(data, preserve_dynamic=True)
        assert result["static"] == "value"
        assert result["dynamic"] == {"__translate__": "Hello", "source": "en"}

    def test_preserve_dynamic_false_flattens_translate(self) -> None:
        data = {
            "dynamic": {"__translate__": "Hello", "source": "en"},
        }
        result = flatten(data, preserve_dynamic=False)
        assert result == {"dynamic.__translate__": "Hello", "dynamic.source": "en"}

    def test_empty_dict(self) -> None:
        assert flatten({}) == {}

    def test_with_parent_prefix(self) -> None:
        data = {"key": "value"}
        result = flatten(data, parent="root")
        assert result == {"root.key": "value"}


# --- unflatten ---

class TestUnflatten:
    def test_simple(self) -> None:
        data = {"a.b.c": "value"}
        result = unflatten(data)
        assert result == {"a": {"b": {"c": "value"}}}

    def test_multiple_keys(self) -> None:
        data = {
            "home.title": "Bienvenido",
            "home.button": "Entrar",
            "about.title": "Acerca de",
        }
        result = unflatten(data)
        assert result == {
            "home": {"title": "Bienvenido", "button": "Entrar"},
            "about": {"title": "Acerca de"},
        }

    def test_roundtrip(self) -> None:
        original = {"a": {"b": {"c": "d"}}, "e": "f"}
        flat = flatten(original)
        restored = unflatten(flat)
        assert restored == original

    def test_empty_dict(self) -> None:
        assert unflatten({}) == {}


# --- read_mapping / write_mapping ---

class TestReadWriteMapping:
    def test_read_json(self, tmp_path: Path) -> None:
        data = {"key": "value"}
        path = tmp_path / "test.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        assert read_mapping(path) == data

    def test_write_json(self, tmp_path: Path) -> None:
        data = {"key": "value", "nested": {"a": 1}}
        path = tmp_path / "out.json"
        write_mapping(path, data)
        assert json.loads(path.read_text()) == data

    def test_unsupported_format_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "test.txt"
        path.write_text("hello", encoding="utf-8")
        with pytest.raises(TranslationFileError, match="Unsupported"):
            read_mapping(path)

    def test_write_unsupported_format_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "test.txt"
        with pytest.raises(TranslationFileError, match="Unsupported"):
            write_mapping(path, {"key": "value"})

    def test_corrupt_json_in_read_mapping(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("{invalid", encoding="utf-8")
        with pytest.raises(TranslationFileError):
            read_mapping(path)

    def test_roundtrip_json(self, tmp_path: Path) -> None:
        data = {"a": {"b": "c"}, "d": [1, 2, 3]}
        path = tmp_path / "roundtrip.json"
        write_mapping(path, data)
        assert read_mapping(path) == data
