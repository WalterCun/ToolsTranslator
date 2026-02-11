#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo de uso de AutoTranslate para traducir un archivo JSON base a varios idiomas.
- Utiliza el archivo de ejemplo incluido en el repositorio: struct_files/en.json
- Escribe las traducciones en examples/output (creado si no existe)
- Requiere que el servicio LibreTranslate esté disponible en http://localhost:5000
"""

from argparse import Namespace
from pathlib import Path
import sys
import requests

# Añadir repo a sys.path para ejecutar el ejemplo sin instalar el paquete
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from bk.core.autotranslate import AutoTranslate  # noqa: E402
from bk.utils import TranslateFile  # noqa: E402


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

    src = ROOT / "struct_files" / "en.json"
    if not src.exists():
        print(f"No se encontró el archivo base: {src}")
        return

    out_dir = Path(__file__).resolve().parent / "output"
    out_dir.mkdir(exist_ok=True)

    info = TranslateFile(src)
    args = Namespace(base=None, langs=["es", "fr"], output=str(out_dir), force=False, overwrite=True)
    auto = AutoTranslate(info, args=args)

    # Ejecuta el proceso de traducción según los argumentos
    auto.worker()
    print(f"Traducciones generadas en: {out_dir}")


if __name__ == "__main__":
    main()
