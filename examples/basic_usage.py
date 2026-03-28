"""Ejemplo básico — Uso mínimo de ToolsTranslator.

Este ejemplo muestra cómo inicializar el Translator y acceder
a traducciones desde archivos JSON.

Requisitos previos:
    Crear locales/es.json con el siguiente contenido:
    {
        "app": {
            "title": "Mi Aplicación",
            "buttons": {
                "save": "Guardar",
                "cancel": "Cancelar"
            }
        },
        "greeting": "¡Hola!"
    }
"""

from pathlib import Path
from translator import Translator

# 1. Inicializar el traductor
trans = Translator(lang="es", directory=Path(__file__).parent / "locales")

# 2. Acceso por atributos (recomendado)
print(trans.app.title)           # "Mi Aplicación"
print(trans.app.buttons.save)    # "Guardar"
print(trans.greeting)            # "¡Hola!"

# 3. Acceso por clave con puntos
print(trans.get("app.title"))    # "Mi Aplicación"
print(trans.get("app.buttons.cancel"))  # "Cancelar"

# 4. Cambiar idioma (si existe en.json)
# trans.change_lang("en")
# print(trans.app.title)  # "My Application"

# 5. Listar idiomas disponibles
print(f"Idiomas disponibles: {trans.available_languages()}")

# 6. Clave con valor por defecto
print(trans.get("missing.key", default="No encontrado"))  # "No encontrado"
