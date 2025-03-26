from pathlib import Path

from utils.extract_info_file import extract_lang_info_from_filename


def test_extract_lang_info_from_filename():
    """Prueba la extracción del idioma desde un archivo"""
    path = Path("../../assets/es.json")
    result = extract_lang_info_from_filename(path)
    expected = {
        "path": path,
        "directory": path.parent,
        "lang": "es",
        "ext": "json",
        "name": "es.json"
    }
    assert result == expected
