import pytest
from pathlib import Path
from translator.core.autotranslate import AutoTranslate, AutoTranslateOptions
from translator.utils.fileinfo import TranslateFile
from translator.adapters.libretranslate import TranslationAdapter

class MockAdapter(TranslationAdapter):
    def available(self) -> tuple[bool, str]:
        return True, "ok"

    def translate(self, text: str, source: str, target: str) -> str:
        return f"[{target}] {text}"
    
    async def translate_async(self, text: str, source: str, target: str) -> str:
        return f"[{target}] {text}"

def test_autotranslate_worker(tmp_path):
    """Test the AutoTranslate worker logic."""
    locale_dir = tmp_path / "locales"
    locale_dir.mkdir()
    
    # Create a source file
    with open(locale_dir / "en.json", "w", encoding="utf-8") as f:
        f.write('{"hello": "world"}')
    
    translate_file = TranslateFile(locale_dir / "en.json")
    options = AutoTranslateOptions(
        langs=["es", "fr"],
        output=locale_dir,
        force=True,
        nested=True
    )
    
    adapter = MockAdapter()
    auto = AutoTranslate(translate_file, options, adapter=adapter)
    
    result = auto.worker()
    
    assert len(result.generated_files) == 2
    assert result.translated_keys == 2
    assert result.failed_keys == 0
    
    # Verify content
    with open(locale_dir / "es.json", "r", encoding="utf-8") as f:
        es_content = f.read()
    assert '"hello": "[es] world"' in es_content
    
    with open(locale_dir / "fr.json", "r", encoding="utf-8") as f:
        fr_content = f.read()
    assert '"hello": "[fr] world"' in fr_content
