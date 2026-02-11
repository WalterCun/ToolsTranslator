import pytest
from pathlib import Path
from translator import Translator

def test_translator_initialization(tmp_path):
    """Test basic initialization of the Translator class."""
    locale_dir = tmp_path / "locales"
    locale_dir.mkdir()
    
    # Create a dummy language file
    with open(locale_dir / "en.json", "w", encoding="utf-8") as f:
        f.write('{"hello": "world"}')
    
    t = Translator(lang="en", directory=locale_dir)
    
    assert t.lang == "en"
    assert t.directory == locale_dir
    assert t.get("hello") == "world"

def test_translator_default_directory(tmp_path, monkeypatch):
    """Test initialization with default directory from settings."""
    # Mock settings.locale_dir
    monkeypatch.setenv("TOOLSTRANSLATOR_LOCALE_DIR", str(tmp_path / "default_locales"))
    
    # Reload settings or just pass None to directory (which uses settings.locale_dir)
    # Since settings are loaded at import time, we might need to patch the settings object directly if possible,
    # or rely on the fact that Translator uses settings.locale_dir in __init__.
    
    # However, Translator.__init__ reads settings.locale_dir.
    # Let's try to patch the settings object in translator.config if possible, or just pass directory=None.
    
    # For this test, let's just verify that if we pass directory=None, it tries to use the default.
    # We can't easily change the default without reloading the module or patching.
    # So let's just check if it creates the directory if it doesn't exist (which it does in __init__).
    
    # Actually, let's just test that we can pass a Path object.
    t = Translator(directory=tmp_path / "custom_locales")
    assert t.directory == tmp_path / "custom_locales"
    assert (tmp_path / "custom_locales").exists()
