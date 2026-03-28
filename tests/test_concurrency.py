"""Tests for thread safety and concurrent access."""

import json
import threading
from pathlib import Path

from translator import Translator


class TestThreadSafety:
    def test_concurrent_reads(self, tmp_path: Path) -> None:
        """Multiple threads reading translations simultaneously should not corrupt data."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        data = {f"key_{i}": f"value_{i}" for i in range(100)}
        (locale_dir / "en.json").write_text(json.dumps(data), encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir)
        results: dict[int, str] = {}
        errors: list[Exception] = []

        def read_key(idx: int) -> None:
            try:
                results[idx] = t.get(f"key_{idx}")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=read_key, args=(i,)) for i in range(100)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        assert not errors, f"Errors in threads: {errors}"
        assert len(results) == 100
        for i in range(100):
            assert results[i] == f"value_{i}"

    def test_concurrent_auto_add_missing_keys(self, tmp_path: Path) -> None:
        """Multiple threads adding missing keys should not corrupt the file."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text("{}", encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir, auto_add_missing_keys=True)
        errors: list[Exception] = []

        def add_key(idx: int) -> None:
            try:
                t.get(f"new_key_{idx}")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=add_key, args=(i,)) for i in range(20)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        assert not errors, f"Errors in threads: {errors}"
        # Verify file is valid JSON with all keys
        content = json.loads((locale_dir / "en.json").read_text())
        assert len(content) == 20
        for i in range(20):
            assert f"new_key_{i}" in content

    def test_concurrent_lang_switch(self, tmp_path: Path) -> None:
        """Switching language from multiple threads should not crash."""
        locale_dir = tmp_path / "locales"
        locale_dir.mkdir()
        (locale_dir / "en.json").write_text('{"key": "Hello"}', encoding="utf-8")
        (locale_dir / "es.json").write_text('{"key": "Hola"}', encoding="utf-8")
        (locale_dir / "fr.json").write_text('{"key": "Bonjour"}', encoding="utf-8")

        t = Translator(lang="en", directory=locale_dir)
        langs = ["en", "es", "fr"]
        errors: list[Exception] = []

        def switch_and_read(lang: str) -> None:
            try:
                t.change_lang(lang)
                _ = t.get("key")
            except Exception as exc:
                errors.append(exc)

        threads = [
            threading.Thread(target=switch_and_read, args=(langs[i % 3],))
            for i in range(30)
        ]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        assert not errors, f"Errors in threads: {errors}"
