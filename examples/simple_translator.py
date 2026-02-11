#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo mínimo de uso de Translator.
- Crea/usa un directorio de idiomas local para guardar traducciones.
- Requiere que el servicio LibreTranslate esté disponible si desea validar idiomas.
"""

from pathlib import Path
import sys
import requests

# Permitir ejecutar sin instalar el paquete (añade el repo a sys.path)
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from bk import Translator  # noqa: E402


def service_available(url: str = "http://localhost:5000") -> bool:
    try:
        requests.get(url, timeout=2)
        return True
    except requests.RequestException:
        return False


def main():
    if not service_available():
        print("LibreTranslate no está disponible en http://localhost:5000. Consulta docs/HOWTO_DOCKER.md para iniciarlo.")
        return

    # Directorio local para idiomas
    langs_dir = Path(__file__).resolve().parent / "langs_output"
    langs_dir.mkdir(exist_ok=True)

    tr = Translator(translations_dir=langs_dir, default_lang="en")

    # Agregar traducción al archivo es.json
    tr.add_trans(key="greeting", lang="es", value="Hola mundo")

    # Cambiar de idioma y leer la clave como atributo
    tr.lang = "es"
    print("greeting (es):", tr.greeting)


if __name__ == "__main__":
    main()
