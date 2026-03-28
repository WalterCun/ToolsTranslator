"""Batch translation — Traducir múltiples textos y archivos.

Este ejemplo muestra cómo:
1. Traducir una lista de textos
2. Generar archivos de idioma completos
3. Usar AutoTranslate para múltiples idiomas

Requiere un servidor LibreTranslate activo o un adapter personalizado.
"""

import json
from pathlib import Path
from translator import Translator

# --- Configuración ---
LOCALES_DIR = Path(__file__).parent / "locales_batch"
LOCALES_DIR.mkdir(exist_ok=True)

# Crear archivo base de ejemplo
base_file = LOCALES_DIR / "en.json"
base_data = {
    "navigation": {
        "home": "Home",
        "about": "About",
        "contact": "Contact"
    },
    "messages": {
        "welcome": "Welcome to our application",
        "goodbye": "Thank you for using our app",
        "error": "An error occurred"
    },
    "buttons": {
        "submit": "Submit",
        "cancel": "Cancel",
        "save": "Save"
    }
}
base_file.write_text(json.dumps(base_data, indent=2, ensure_ascii=False), encoding="utf-8")

# --- Ejemplo 1: Traducir lista de textos ---
print("=== Traducción de lista ===")

# Usamos un adapter mock para el ejemplo
class MockAdapter:
    def available(self):
        return True, "ok"
    def translate(self, text, source, target):
        return f"[{target}] {text}"

trans = Translator(lang="en", directory=LOCALES_DIR, adapter=MockAdapter())

texts = ["Hello", "Goodbye", "Thank you", "Please wait"]
for text in texts:
    translated = trans.translate(text, source="en", target="es")
    print(f"  {text} → {translated}")

# --- Ejemplo 2: Generar archivo de idioma ---
print("\n=== Generar archivo de idioma ===")

result = trans.generate_language_file(
    base_file=base_file,
    target_lang="es",
    output=LOCALES_DIR / "es.json",
    source_lang="en"
)

print(f"  Traducciones generadas: {len(result)}")
for key, value in list(result.items())[:3]:
    print(f"  {key} = {value}")
print("  ...")

# --- Ejemplo 3: AutoTranslate (múltiples idiomas) ---
print("\n=== AutoTranslate ===")

from translator.core.autotranslate import AutoTranslate, AutoTranslateOptions
from translator.utils.fileinfo import TranslateFile

options = AutoTranslateOptions(
    langs=["fr", "de"],
    overwrite=True,
    output=LOCALES_DIR
)

file_info = TranslateFile(base_file)
auto = AutoTranslate(file_info, options, adapter=MockAdapter())
result = auto.worker()

print(f"  Archivos generados: {result.generated_files}")
print(f"  Claves traducidas: {result.translated_keys}")
print(f"  Claves fallidas: {result.failed_keys}")

# Verificar archivos generados
for lang in ["es", "fr", "de"]:
    lang_file = LOCALES_DIR / f"{lang}.json"
    if lang_file.exists():
        data = json.loads(lang_file.read_text())
        print(f"  {lang}.json: {len(data)} secciones")
