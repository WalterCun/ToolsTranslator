"""Unit tests for Translator internal helpers — deep_get, deep_set, TranslationProxy."""

import json
from pathlib import Path

import pytest

from translator import Translator


# --- _deep_get / _deep_set ---

class TestDeepGet:
    def test_simple_key(self) -> None:
        data = {"key": "value"}
        assert Translator._deep_get(data, "key") == "value"

    def test_nested_key(self) -> None:
        data = {"a": {"b": {"c": "deep"}}}
        assert Translator._deep_get(data, "a.b.c") == "deep"

    def test_missing_key_returns_none(self) -> None:
        data = {"key": "value"}
        assert Translator._deep_get(data, "missing") is None

    def test_missing_nested_key_returns_none(self) -> None:
        data = {"a": {"b": "value"}}
        assert Translator._deep_get(data, "a.x") is None

    def test_intermediate_not_dict_returns_none(self) -> None:
        data = {"a": "string_value"}
        assert Translator._deep_get(data, "a.b") is None


class TestDeepSet:
    def test_simple_key(self) -> None:
        data: dict = {}
        Translator._deep_set(data, "key", "value")
        assert data == {"key": "value"}

    def test_nested_key(self) -> None:
        data: dict = {}
        Translator._deep_set(data, "a.b.c", "value")
        assert data == {"a": {"b": {"c": "value"}}}

    def test_overwrites_non_dict_intermediate(self) -> None:
        data = {"a": "string"}
        Translator._deep_set(data, "a.b", "value")
        assert data == {"a": {"b": "value"}}

    def test_preserves_existing_keys(self) -> None:
        data = {"a": {"existing": "keep"}}
        Translator._deep_set(data, "a.new", "added")
        assert data == {"a": {"existing": "keep", "new": "added"}}


# --- TranslationProxy ---

class TestTranslationProxy:
    def test_proxy_str_for_dict(self, tmp_path: Path) -> None:
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text(
            json.dumps({"section": {"key": "value"}}), encoding="utf-8"
        )
        t = Translator(lang="en", directory=locale_dir)
        # Accessing a dict returns a proxy, str() should resolve
        proxy = t.section
        assert str(proxy)  # should not raise

    def test_proxy_leaf_returns_string(self, tmp_path: Path) -> None:
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text(
            json.dumps({"key": "hello"}), encoding="utf-8"
        )
        t = Translator(lang="en", directory=locale_dir)
        assert t.key == "hello"

    def test_proxy_deep_access(self, tmp_path: Path) -> None:
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text(
            json.dumps({"a": {"b": {"c": "deep"}}}), encoding="utf-8"
        )
        t = Translator(lang="en", directory=locale_dir)
        assert t.a.b.c == "deep"

    def test_proxy_missing_key_returns_proxy(self, tmp_path: Path) -> None:
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text("{}", encoding="utf-8")
        t = Translator(lang="en", directory=locale_dir)
        # Accessing non-existent key returns proxy (not crash)
        proxy = t.nonexistent
        assert str(proxy) == "nonexistent"  # missing_key_behavior="key" default
