"""
Example: Changing Language

This example demonstrates:
1. Loading multiple language files.
2. Switching the active language at runtime.
3. Verifying that translations update accordingly.
"""

import shutil
import json
from pathlib import Path
from translator import Translator

LOCALE_DIR = Path("locales")
if LOCALE_DIR.exists():
    shutil.rmtree(LOCALE_DIR)
LOCALE_DIR.mkdir(parents=True, exist_ok=True)

# Create an English file
en_data = {
    "greeting": "Hello",
    "farewell": "Goodbye"
}
with open(LOCALE_DIR / "en.json", "w", encoding="utf-8") as f:
    json.dump(en_data, f)

# Create a Spanish file
es_data = {
    "greeting": "Hola",
    "farewell": "Adiós"
}
with open(LOCALE_DIR / "es.json", "w", encoding="utf-8") as f:
    json.dump(es_data, f)

def main():
    print("--- Change Language Example ---")

    # Initialize with English
    t = Translator(lang="en", directory=LOCALE_DIR)
    print(f"Current language: {t.lang}")
    print(f"Greeting (en): {t.greeting}")  # Expected: Hello

    # Switch to Spanish
    print("Switching language to 'es'...")
    t.change_lang("es")
    print(f"Current language: {t.lang}")
    print(f"Greeting (es): {t.greeting}")  # Expected: Hola

    # Switch back to English using property setter
    print("Switching language to 'en' via property...")
    t.lang = "en"
    print(f"Current language: {t.lang}")
    print(f"Farewell (en): {t.farewell}")  # Expected: Goodbye

    # Cleanup
    if LOCALE_DIR.exists():
        shutil.rmtree(LOCALE_DIR)

if __name__ == "__main__":
    main()
