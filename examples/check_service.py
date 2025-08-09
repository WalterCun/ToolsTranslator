#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprueba si el servicio LibreTranslate está disponible en http://localhost:5000.
Este ejemplo NO inicia Docker ni contenedores; solo realiza una solicitud HTTP.
"""

import requests


def main():
    try:
        r = requests.get("http://localhost:5000", timeout=3)
        if r.status_code == 200:
            print("LibreTranslate está disponible en http://localhost:5000")
        else:
            print(f"Respuesta recibida pero no OK: {r.status_code}")
    except requests.RequestException as e:
        print("LibreTranslate no está disponible. Consulta docs/HOWTO_DOCKER.md para iniciarlo.")
        print(f"Detalle: {e}")


if __name__ == "__main__":
    main()
