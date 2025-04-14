# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/parses/yaml.py """

from typing import Union, List, Dict

import yaml


class YAML:
    """
    Clase para gestionar archivos YAML.
    Incluye funciones para serializar/deserializar datos y guardar/cargar archivos YAML.
    """

    def __init__(self, file_path: str = None):
        """
        Constructor para inicializar un objeto de gestión de YAML.

        :param file_path: Ruta del archivo YAML (opcional).
        """
        self.file_path = file_path

    @staticmethod
    def serializer_yaml(data: Union[Dict, List], path: str = "") -> list[dict]:
        """
        Serializa datos en una estructura YAML usando una lógica externa (JSON en este caso).

        :param data: Datos en formato dict o lista.
        :param path: Ruta base (opcional).
        :return: Lista de tuplas serializada.
        """
        # Simula lógica de serialización usando un serializer externo.
        from parses.json import JSON
        return JSON.serializer_json(data, path)

    @staticmethod
    def deserializer_yaml(entries: List[Dict]) -> Union[Dict, List]:
        """
        Deserializa una estructura de datos en un diccionario de Python.

        :param entries: Lista de tuplas serializada.
        :return: Diccionario deserializado.
        """
        from parses.json import JSON
        return JSON.deserializar_json(entries)

    def get_content_yaml_file(self, file_path: str = None) -> dict:
        """
        Carga el contenido de un archivo YAML y lo convierte en un diccionario de Python.

        :param file_path: Ruta del archivo YAML (si no se proporciona, se utiliza self.file_path).
        :return: Diccionario con los datos cargados.
        """
        file_path = file_path or self.file_path
        if not file_path:
            raise ValueError("No se proporcionó una ruta de archivo YAML.")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
            return data
        except Exception as e:
            print(f"Error al cargar el archivo YAML: {e}")
            raise

    def save_yaml_file(self, data: dict, file_path: str = None):
        """
        Guarda un diccionario en un archivo YAML.

        :param data: Diccionario con los datos a guardar.
        :param file_path: Ruta del archivo YAML (si no se proporciona, se utiliza self.file_path).
        """
        file_path = file_path or self.file_path
        if not file_path:
            raise ValueError("No se proporcionó una ruta de archivo YAML.")

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                yaml.dump(data, file, sort_keys=False, allow_unicode=True)
            print(f"El diccionario se guardó correctamente en '{file_path}'.")
        except Exception as e:
            print(f"Error al guardar el diccionario en YAML: {e}")
            raise

# Ejemplo de uso
# if __name__ == "__main__":
#     gestor_yaml = YAML("archivo_ejemplo.yaml")
#
#     # Cargar datos desde un archivo YAML
#     try:
#         datos = gestor_yaml.get_content_yaml_file()
#         print("Contenido cargado:", datos)
#     except Exception as e:
#         print(f"Error al obtener contenido del archivo: {e}")
#
#     # Guardar un diccionario como archivo YAML
#     datos_a_guardar = {"nombre": "Juan", "edad": 30, "ciudad": "Madrid"}
#     try:
#         gestor_yaml.save_yaml_file(datos_a_guardar)
#     except Exception as e:
#         print(f"Error al guardar contenido en el archivo: {e}")
