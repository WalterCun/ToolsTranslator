"""Manejo de errores — Qué pasa cuando las cosas fallan.

Este ejemplo muestra cómo manejar cada tipo de error que puede ocurrir:
1. Archivo de idioma corrupto
2. Idioma no disponible
3. Servicio de traducción caído
4. Dependencia opcional faltante
"""

import json
from pathlib import Path
from translator import Translator
from translator.exceptions import (
    TranslationFileError,
    LanguageNotAvailableError,
    ServiceUnavailableError,
    ExtraNotInstalledError,
)

LOCALES_DIR = Path(__file__).parent / "locales_errors"
LOCALES_DIR.mkdir(exist_ok=True)

# --- Ejemplo 1: Archivo JSON corrupto ---
print("=== Archivo corrupto ===")

corrupt_file = LOCALES_DIR / "bad.json"
corrupt_file.write_text('{"hello": "incomplete', encoding="utf-8")

try:
    trans = Translator(lang="bad", directory=LOCALES_DIR)
except TranslationFileError as e:
    print(f"  ✖ Archivo corrupto: {e}")
    print(f"    → Solución: Verifica que el JSON sea válido")

# Archivo válido para los siguientes ejemplos
(LOCALES_DIR / "es.json").write_text('{"key": "valor"}', encoding="utf-8")

# --- Ejemplo 2: Idioma no disponible ---
print("\n=== Idioma no disponible ===")

trans = Translator(lang="es", directory=LOCALES_DIR, fallback_lang="")

try:
    trans.change_lang("fr")  # No existe fr.json
except LanguageNotAvailableError as e:
    print(f"  ✖ {e}")
    print(f"    → Idiomas disponibles: {trans.available_languages()}")
    print(f"    → Solución: Crea fr.json o usa fallback_lang='es'")

# --- Ejemplo 3: Servicio de traducción caído ---
print("\n=== Servicio caído ===")

# Adapter que siempre falla
class BrokenAdapter:
    def available(self):
        return False, "Connection refused"

    def translate(self, text, source, target):
        raise ServiceUnavailableError("El servidor de traducción no responde")

trans_broken = Translator(lang="es", directory=LOCALES_DIR, adapter=BrokenAdapter())

try:
    result = trans_broken.translate("Hola", target="en")
except ServiceUnavailableError as e:
    print(f"  ✖ Servicio no disponible: {e}")
    print(f"    → Solución: Ejecuta 'toolstranslator install' o 'toolstranslator restart'")

# --- Ejemplo 4: Traducción con fallback ---
print("\n=== Fallback en traducción ===")

result = trans_broken.translate("Hola", target="en", fallback="TRADUCCIÓN FALLIDA")
print(f"  translate('Hola', fallback='TRADUCCIÓN FALLIDA') = '{result}'")

result = trans_broken.translate("Hola", target="en", fallback=lambda t: f"[NO TRADUCIDO: {t}]")
print(f"  translate('Hola', fallback=lambda) = '{result}'")

# --- Ejemplo 5: Fallback de idioma ---
print("\n=== Fallback de idioma ===")

trans_fallback = Translator(lang="es", directory=LOCALES_DIR, fallback_lang="es")
trans_fallback.change_lang("de")  # No existe de.json, usa es.json
print(f"  Idioma activo: {trans_fallback.lang}")
print(f"  get('key') (desde fallback): '{trans_fallback.get('key')}'")

# --- Ejemplo 6: Dependencia opcional YAML ---
print("\n=== Dependencia opcional ===")

try:
    from translator.handlers.yaml_handler import YamlHandler
    print("  ✔ PyYAML instalado — soporte YAML disponible")
except ExtraNotInstalledError:
    print("  ✖ PyYAML no instalado")
    print("    → Solución: pip install toolstranslator[yml]")

# --- Ejemplo 7: Verificar disponibilidad del adapter ---
print("\n=== Verificar disponibilidad ===")

from translator.adapters.libretranslate import LibreTranslateClient

client = LibreTranslateClient(base_url="http://localhost:5000")
ok, reason = client.available()
print(f"  LibreTranslate disponible: {ok}")
if not ok:
    print(f"  Razón: {reason}")
    print("  → Solución: toolstranslator install")
