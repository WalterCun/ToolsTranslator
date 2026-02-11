"""
Example: AutoTranslate (Simulated)

This example demonstrates:
1. Using the AutoTranslate functionality to generate language files.
2. Simulating the translation process (since we don't have a real server).
3. Handling nested keys and file generation.
"""

import shutil
import json
from pathlib import Path
from translator.core.autotranslate import AutoTranslate, AutoTranslateOptions
from translator.utils.fileinfo import TranslateFile
from translator.adapters.libretranslate import TranslationAdapter

# Mock Adapter for simulation
class MockAdapter(TranslationAdapter):
    def available(self) -> tuple[bool, str]:
        return True, "ok"

    def translate(self, text: str, source: str, target: str) -> str:
        return f"[{target}] {text}"

LOCALE_DIR = Path("locales")
if LOCALE_DIR.exists():
    shutil.rmtree(LOCALE_DIR)
LOCALE_DIR.mkdir(parents=True, exist_ok=True)

# Create a source file (en.json)
en_data = {
    "hello": "Hello",
    "welcome": "Welcome",
    "user": {
        "name": "Name"
    }
}
with open(LOCALE_DIR / "en.json", "w", encoding="utf-8") as f:
    json.dump(en_data, f)

def main():
    print("--- AutoTranslate Example (Simulated) ---")

    # 1. Setup AutoTranslate
    translate_file = TranslateFile(LOCALE_DIR / "en.json")
    options = AutoTranslateOptions(
        langs=["es", "fr"],  # Target languages
        output=LOCALE_DIR,   # Output directory
        force=True,          # Force overwrite
        nested=True          # Maintain a nested structure
    )
    
    # Use our MockAdapter to simulate translation
    adapter = MockAdapter()
    auto = AutoTranslate(translate_file, options, adapter=adapter)

    # 2. Run AutoTranslate
    print("Running AutoTranslate...")
    result = auto.worker()

    # 3. Verify Results
    print(f"Generated files: {result.generated_files}")
    print(f"Total keys: {result.total_keys}")
    print(f"Translated keys: {result.translated_keys}")
    print(f"Failed keys: {result.failed_keys}")

    # Check the generated Spanish file
    es_file = LOCALE_DIR / "es.json"
    if es_file.exists():
        with open(es_file, "r", encoding="utf-8") as f:
            es_data = json.load(f)
        print(f"Spanish content: {es_data}")
        # Expected: {"hello": "[es] Hello", "welcome": "[es] Welcome", "user": {"name": "[es] Name"}}
    else:
        print("Spanish file not generated!")

    # Check the generated French file
    fr_file = LOCALE_DIR / "fr.json"
    if fr_file.exists():
        with open(fr_file, "r", encoding="utf-8") as f:
            fr_data = json.load(f)
        print(f"French content: {fr_data}")
        # Expected: {"hello": "[fr] Hello", "welcome": "[fr] Welcome", "user": {"name": "[fr] Name"}}
    else:
        print("French file not generated!")

    # Cleanup
    if LOCALE_DIR.exists():
        shutil.rmtree(LOCALE_DIR)

if __name__ == "__main__":
    main()
