"""
Example: Handling Missing Keys

This example demonstrates:
1. Default behavior when a key is missing.
2. Customizing the missing key behavior (e.g., returning a message).
3. Using `auto_add_missing_keys` to automatically add missing keys to the language file.
"""

import shutil
import json
from pathlib import Path
from translator import Translator

LOCALE_DIR = Path("locales")
if LOCALE_DIR.exists():
    shutil.rmtree(LOCALE_DIR)
LOCALE_DIR.mkdir(parents=True, exist_ok=True)

# Create a basic language file
en_data = {
    "existing_key": "I exist"
}
with open(LOCALE_DIR / "en.json", "w", encoding="utf-8") as f:
    json.dump(en_data, f)

def main():
    print("--- Missing Keys Example ---")

    # 1. Default Behavior (returns the key itself)
    t = Translator(lang="en", directory=LOCALE_DIR, missing_key_behavior="key")
    print(f"Missing key (default): {t.get('non_existent_key')}")  # Expected: non_existent_key

    # 2. Custom Behavior (returns a message)
    t_msg = Translator(lang="en", directory=LOCALE_DIR, missing_key_behavior="message")
    print(f"Missing key (message): {t_msg.get('another_missing_key')}")  # Expected: Missing translation

    # 3. Auto Add Missing Keys
    print("\n--- Auto Add Missing Keys ---")
    # Enable auto_add_missing_keys
    t_auto = Translator(lang="en", directory=LOCALE_DIR, auto_add_missing_keys=True)
    
    missing_key = "newly_added_key"
    print(f"Accessing missing key '{missing_key}'...")
    value = t_auto.get(missing_key)
    print(f"Value returned: {value}")  # Expected: TODO: agregar traducción (or similar default template)

    # Verify that the key was added to the file
    with open(LOCALE_DIR / "en.json", "r", encoding="utf-8") as f:
        updated_data = json.load(f)
    
    if missing_key in updated_data:
        print(f"SUCCESS: Key '{missing_key}' was added to en.json.")
        print(f"Content in file: {updated_data[missing_key]}")
    else:
        print(f"FAILURE: Key '{missing_key}' was NOT added to en.json.")

    # Cleanup
    # if LOCALE_DIR.exists():
    #     shutil.rmtree(LOCALE_DIR)

if __name__ == "__main__":
    main()
