import pytest
from pathlib import Path
from translator import Translator
from translator.exceptions import LanguageNotAvailableError

def test_language_switch(tmp_path):
    """Test switching languages at runtime."""
    locale_dir = tmp_path / "locales"
    locale_dir.mkdir()
    
    # Create English file
    with open(locale_dir / "en.json", "w", encoding="utf-8") as f:
        f.write('{"greeting": "Hello"}')
    
    # Create Spanish file
    with open(locale_dir / "es.json", "w", encoding="utf-8") as f:
        f.write('{"greeting": "Hola"}')
    
    t = Translator(lang="en", directory=locale_dir)
    assert t.lang == "en"
    assert t.greeting == "Hello"
    
    # Switch to Spanish
    t.change_lang("es")
    assert t.lang == "es"
    assert t.greeting == "Hola"
    
    # Switch back to English via property
    t.lang = "en"
    assert t.lang == "en"
    assert t.greeting == "Hello"

def test_language_switch_missing_file(tmp_path):
    """Test switching to a language that doesn't exist."""
    locale_dir = tmp_path / "locales"
    locale_dir.mkdir()
    
    with open(locale_dir / "en.json", "w", encoding="utf-8") as f:
        f.write('{"greeting": "Hello"}')
    
    t = Translator(lang="en", directory=locale_dir)
    
    # Try to switch to a non-existent language
    # This should raise LanguageNotAvailableError
    with pytest.raises(LanguageNotAvailableError):
        t.change_lang("fr")
