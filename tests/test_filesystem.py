import pytest
from pathlib import Path
from translator import Translator

def test_filesystem_operations(tmp_path):
    """Test file creation and reading."""
    locale_dir = tmp_path / "locales"
    locale_dir.mkdir()
    
    # Create a file manually
    with open(locale_dir / "en.json", "w", encoding="utf-8") as f:
        f.write('{"key": "value"}')
    
    t = Translator(lang="en", directory=locale_dir)
    assert t.get("key") == "value"
    
    # Test writing a new file (e.g., via generate_language_file)
    # This is a bit more complex as it involves translation logic.
    # Let's just test that we can read from different file formats if supported.
    
    # YAML support (if installed)
    try:
        import yaml
        with open(locale_dir / "es.yaml", "w", encoding="utf-8") as f:
            f.write('key: valor')
        t.change_lang("es")
        assert t.get("key") == "valor"
    except ImportError:
        pytest.skip("YAML support not installed")

def test_directory_creation(tmp_path):
    """Test that the directory is created if it doesn't exist."""
    locale_dir = tmp_path / "new_locales"
    assert not locale_dir.exists()
    
    t = Translator(directory=locale_dir)
    assert locale_dir.exists()
