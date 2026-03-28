"""Configuración personalizada — Variables de entorno, adapter custom.

Este ejemplo muestra cómo configurar ToolsTranslator de diferentes formas:
1. Variables de entorno
2. Parámetros del constructor
3. Adapter personalizado
4. Configuración de logging
"""

import os
import json
from pathlib import Path

# --- Ejemplo 1: Variables de entorno ---
print("=== Variables de entorno ===")

# Estas se leen al importar el módulo. Para este ejemplo,
# las configuramos antes de importar.
os.environ["TOOLSTRANSLATOR_BASE_URL"] = "http://localhost:5000"
os.environ["TOOLSTRANSLATOR_TIMEOUT"] = "15"
os.environ["TOOLSTRANSLATOR_LOG_LEVEL"] = "DEBUG"
os.environ["TOOLSTRANSLATOR_MISSING_KEY"] = "message"

from translator.config import settings

print(f"  base_url: {settings.base_url}")
print(f"  timeout: {settings.timeout}")
print(f"  log_level: {settings.log_level}")
print(f"  missing_key_behavior: {settings.missing_key_behavior}")

# --- Ejemplo 2: Parámetros del constructor ---
print("\n=== Parámetros del constructor ===")

LOCALES_DIR = Path(__file__).parent / "locales_custom"
LOCALES_DIR.mkdir(exist_ok=True)
(LOCALES_DIR / "es.json").write_text(
    json.dumps({"app": {"title": "Mi App"}}), encoding="utf-8"
)

from translator import Translator

trans = Translator(
    lang="es",
    directory=LOCALES_DIR,
    timeout=5.0,                    # Timeout más corto
    missing_key_behavior="message", # Claves faltantes muestran mensaje
    auto_add_missing_keys=True,     # Auto-agregar claves nuevas
    missing_value_template="PENDIENTE",  # Template personalizado
    fallback_lang="es",             # Fallback al mismo idioma
)

print(f"  Idioma: {trans.lang}")
print(f"  Directorio: {trans.directory}")
print(f"  app.title: {trans.app.title}")
print(f"  missing (behavior=message): {trans.get('nonexistent')}")

# --- Ejemplo 3: Adapter personalizado ---
print("\n=== Adapter personalizado ===")

class TranslationMemory:
    """Adapter que usa un diccionario como memoria de traducciones."""

    def __init__(self):
        self.memory = {
            ("Hello", "en", "es"): "Hola",
            ("Goodbye", "en", "es"): "Adiós",
            ("Thank you", "en", "es"): "Gracias",
        }

    def available(self) -> tuple[bool, str]:
        return True, "Translation memory ready"

    def translate(self, text: str, source: str, target: str) -> str:
        key = (text, source, target)
        if key in self.memory:
            return self.memory[key]
        return f"[{target}] {text}"  # Fallback

trans_custom = Translator(lang="es", directory=LOCALES_DIR, adapter=TranslationMemory())
print(f"  Hello → {trans_custom.translate('Hello', source='en', target='es')}")
print(f"  Goodbye → {trans_custom.translate('Goodbye', source='en', target='es')}")
print(f"  Unknown → {trans_custom.translate('Unknown', source='en', target='es')}")

# --- Ejemplo 4: Configuración de logging ---
print("\n=== Logging ===")

import logging

# Cambiar nivel en runtime
logger = logging.getLogger("translator")
logger.setLevel(logging.DEBUG)

# Crear un handler que capture los logs
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

# Ahora las operaciones mostrarán logs DEBUG
trans_debug = Translator(lang="es", directory=LOCALES_DIR)
trans_debug.change_lang("es")  # Muestra "Language changed: es -> es"
