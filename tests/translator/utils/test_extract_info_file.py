from pathlib import Path
import pytest
from translator.utils.extract_info_file import TranslateFile

@pytest.fixture
def file_path(tmp_path):
    # Create a dummy file for testing
    p = tmp_path / "es.json"
    p.write_text('{"hello": "world"}')
    return p

def test_translate_file_init(file_path):
    """Tests the initialization of the TranslateFile class."""
    tf = TranslateFile(file_path)
    assert tf.path == file_path
    assert tf.directory == file_path.parent
    assert tf.ext == "json"
    assert tf.name == "es"
    assert tf.content == {"hello": "world"}
