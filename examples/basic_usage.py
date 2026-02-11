"""
Example: Basic Usage of Translator

This example demonstrates:
1. Initializing the Translator with a specific language.
2. Accessing translations using the `get` method.
3. Accessing translations using attribute access (proxy).
4. Handling nested keys.
"""

import shutil
from pathlib import Path
from translator import Translator

# Setup temporary locale directory for the example
LOCALE_DIR = Path("locales")
if LOCALE_DIR.exists():
    shutil.rmtree(LOCALE_DIR)
LOCALE_DIR.mkdir(parents=True, exist_ok=True)

print(LOCALE_DIR.resolve())

# Create a sample language file (es.json)
import json
es_data = {
    "hello": "Hola",
    "welcome": "Bienvenido",
    "user": {
        "name": "Nombre",
        "profile": {
            "title": "Perfil de Usuario"
        }
    }
}
with open(LOCALE_DIR / "es.json", "w", encoding="utf-8") as f:
    json.dump(es_data, f)

def main():
    print("--- Basic Usage Example ---")

    # 1. Initialize Translator
    # We specify the directory where our language files are located.
    # We set the initial language to 'es' (Spanish).
    t = Translator(lang="es", directory=LOCALE_DIR)
    print(f"Translator initialized with language: {t.lang}")

    # 2. Access using get()
    hello = t.get("hello")
    print(f"t.get('hello'): {hello}")  # Expected: Hola

    # 3. Access using attributes (Proxy)
    welcome = t.welcome
    print(f"t.welcome: {welcome}")    # Expected: Bienvenido

    # 4. Nested keys
    user_name = t.user.name
    print(f"t.user.name: {user_name}") # Expected: Nombre
    
    profile_title = t.get("user.profile.title")
    print(f"t.get('user.profile.title'): {profile_title}") # Expected: Perfil de Usuario

    # Cleanup
    if LOCALE_DIR.exists():
        shutil.rmtree(LOCALE_DIR)

if __name__ == "__main__":
    main()
