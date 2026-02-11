import pytest
import json
from pathlib import Path
from translator import Translator

def test_missing_key_default(tmp_path):
    """Test default behavior for missing keys (returns the key)."""
    locale_dir = tmp_path / "locales"
    locale_dir.mkdir()
    with open(locale_dir / "en.json", "w", encoding="utf-8") as f:
        f.write('{}')
    
    t = Translator(lang="en", directory=locale_dir, missing_key_behavior="key")
    assert t.get("missing") == "missing"

def test_missing_key_message(tmp_path):
    """Test 'message' behavior for missing keys."""
    locale_dir = tmp_path / "locales"
    locale_dir.mkdir()
    with open(locale_dir / "en.json", "w", encoding="utf-8") as f:
        f.write('{}')
    
    t = Translator(lang="en", directory=locale_dir, missing_key_behavior="message")
    assert t.get("missing") == "Missing translation"

def test_auto_add_missing_keys(tmp_path):
    """Test that missing keys are added to the file when enabled."""
    locale_dir = tmp_path / "locales"
    locale_dir.mkdir()
    json_file = locale_dir / "en.json"
    with open(json_file, "w", encoding="utf-8") as f:
        f.write('{"existing": "value"}')
    
    t = Translator(lang="en", directory=locale_dir, auto_add_missing_keys=True)
    
    # Access missing key
    val = t.get("new_key")
    
    # Should return the template (default: "TODO: agregar traducción")
    assert val == "TODO: agregar traducción"
    
    # Verify file content
    with open(json_file, "r", encoding="utf-8") as f:
        content = json.load(f)
    assert "new_key" in content
    assert content["new_key"] == "TODO: agregar traducción"
