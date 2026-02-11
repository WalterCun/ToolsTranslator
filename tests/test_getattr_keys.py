import pytest
from pathlib import Path
from translator import Translator

def test_getattr_access(tmp_path):
    """Test accessing translations via attributes."""
    locale_dir = tmp_path / "locales"
    locale_dir.mkdir()
    
    data = """
    {
        "simple": "value",
        "nested": {
            "key": "nested_value",
            "deep": {
                "key": "deep_value"
            }
        }
    }
    """
    with open(locale_dir / "en.json", "w", encoding="utf-8") as f:
        f.write(data)
    
    t = Translator(lang="en", directory=locale_dir)
    
    assert t.simple == "value"
    assert t.nested.key == "nested_value"
    assert t.nested.deep.key == "deep_value"

def test_getattr_proxy_string_representation(tmp_path):
    """Test that the proxy object converts to string correctly."""
    locale_dir = tmp_path / "locales"
    locale_dir.mkdir()
    
    with open(locale_dir / "en.json", "w", encoding="utf-8") as f:
        f.write('{"key": "value"}')
    
    t = Translator(lang="en", directory=locale_dir)
    
    # t.key returns a string directly if it's a leaf node?
    # Let's check the implementation.
    # _resolve_attr returns TranslationProxy or str.
    # If it's a value, it calls _resolve_dynamic_value which returns str.
    
    assert str(t.key) == "value"
    assert f"{t.key}" == "value"
