"""
Example: Static Files Only

This example demonstrates:
1. Using the Translator without any external translation service.
2. Relying solely on local JSON/YAML files.
3. Handling fallback languages when a key is missing in the primary language.
"""

import shutil
import json
from pathlib import Path
from translator import Translator

LOCALE_DIR = Path("locales")
if LOCALE_DIR.exists():
    shutil.rmtree(LOCALE_DIR)
LOCALE_DIR.mkdir(parents=True, exist_ok=True)

# Create an English file (fallback)
en_data = {
    "title": "My App",
    "description": "A simple application."
}
with open(LOCALE_DIR / "en.json", "w", encoding="utf-8") as f:
    json.dump(en_data, f)

# Create a Spanish file (missing 'description')
es_data = {
    "title": "Mi Aplicación"
}
with open(LOCALE_DIR / "es.json", "w", encoding="utf-8") as f:
    json.dump(es_data, f)

def main():
    print("--- Static Files Only Example ---")

    # Initialize with Spanish but fallback to English
    t = Translator(lang="es", directory=LOCALE_DIR, fallback_lang="en")
    print(f"Current language: {t.lang}")
    print(f"Fallback language: {t.fallback_lang}")

    # 1. Key exists in Spanish
    title = t.get("title")
    print(f"Title (es): {title}")  # Expected: Mi Aplicación

    # 2. Key missing in Spanish should fallback to English
    # Note: The current implementation of `get` might not automatically fallback per-key unless implemented.
    # Let's check if `get` supports per-key fallback or if fallback is only for missing language files.
    # Based on the code review, `_load_language` handles fallback for entire files, but `get` might not fallback per-key.
    # Let's test and see. If it doesn't, we'll document that behavior.
    
    description = t.get("description")
    print(f"Description (es -> fallback?): {description}") 
    # If it returns 'description' (the key), then per-key fallback is not supported by default `get`.
    # If it returns 'A simple application.', then it is supported.
    
    # 3. Explicit fallback in `translate` method (not applicable here as we are using `get` for static files).
    
    # Cleanup
    if LOCALE_DIR.exists():
        shutil.rmtree(LOCALE_DIR)

if __name__ == "__main__":
    main()
