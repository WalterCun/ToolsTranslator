import unittest
from pathlib import Path

from utils.extract_info_file import extract_lang_info_from_filename


class TestUtils(unittest.TestCase):

    def test_extract_lang_info_from_filename(self):
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
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
