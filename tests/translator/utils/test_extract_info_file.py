from pathlib import Path

from bk.utils.extract_info_file import TranslateFile


def test_extract_lang_info_from_filename():
    """Prueba la extracción del idioma desde un archivo"""
    path = Path("../../assets/es.json")
    
    # Usar la clase TranslateFile para extraer la información
    translate_file = TranslateFile(path)
    
    # Construir el resultado usando las propiedades de la clase
    result = {
        "path": translate_file.path,
        "directory": translate_file.directory,
        "lang": translate_file.name,  # name es el stem del archivo (idioma)
        "ext": translate_file.ext,
        "name": translate_file.path.name
    }
    
    expected = {
        "path": path,
        "directory": path.parent,
        "lang": "es",
        "ext": "json",
        "name": "es.json"
    }
    assert result == expected