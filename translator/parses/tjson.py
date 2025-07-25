# !/usr/bin/env python3
# -*- coding: utf-8 -*-
""" translator/parses/json.py """
import json
import logging
from pathlib import Path
from typing import Union, Dict, List, Tuple

log = logging.getLogger(__name__)

class JSON:
    """
        Clase para gestionar archivos JSON.
        Incluye funciones para cargar, guardar, serializar y deserializar datos en formato JSON.
        """

    def __init__(self, file_path: str = None):
        """
        Constructor para inicializar un objeto de gestión de JSON.

        :param file_path: Ruta del archivo JSON (opcional).
        """
        self.file_path = file_path

    def serializer_json(self, data: Union[Dict, List], path: str = "") -> List[Tuple[str, str]]:
        """
        Serializa datos a formato intermedio.

        :param data: Datos en formato dict o lista.
        :param path: Ruta base asociada (puede usarse como ID o clave compuesta).
        :return: Lista serializada en formato intermedio (ejemplo para lógica personalizada).
        """
        # Lógica personalizada de serialización (puedes ajustar según necesidades)
        text_entries = []

        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                text_entries.extend(self.serializer_json(value, new_path))

        elif isinstance(data, list):
            for index, item in enumerate(data):
                new_path = f"{path}[{index}]"
                text_entries.extend(self.serializer_json(item, new_path))

        elif isinstance(data, str):
            text_entries.append((path, data))

        return text_entries

    @staticmethod
    def deserializar_json(entries: List[tuple[str, str]] or Dict[str,str]) -> list[tuple[
        str, str]] or dict or None:
        """
        Reconstruye una estructura JSON de diccionarios anidados a partir de una lista de tuplas (ruta, valor).

        :param entries: Lista de tuplas con (ruta, valor).
        :return: Diccionario que representa la estructura JSON reconstruida.
        """

        def set_nested_value(data: dict, keys: List[str], value: str):
            """
            Sets a nested value in a dictionary by traversing the keys specified in the
            list. If a key does not exist at any level, a new dictionary is created at
            that level.

            :param data: The dictionary where the nested value should be set.
            :type data: dict
            :param keys: A list of keys specifying the path to the value in the nested
                structure. Only the last key in the list will be assigned the specified
                value.
            :type keys: List[str]
            :param value: The value to assign to the specified nested key path in the
                dictionary.
            :type value: str
            :return: None
            """
            for key in keys[:-1]:
                # Si la clave no existe, crea un nuevo diccionario en ese nivel
                if key not in data or not isinstance(data[key], dict):
                    data[key] = {}
                data = data[key]
            # Establece el valor en la última clave
            data[keys[-1]] = value

        def parse_path(path: str) -> List[str]:
            """
            Convierte una ruta de texto en una lista de claves para un diccionario anidado.
            Por ejemplo, "menu.services.options" -> ["menu", "services", "options"].

            :param path: Ruta de texto (e.g., "menu.services.options").
            :return: Lista de claves jerárquicas.
            """
            return path.split('.')

        # Diccionario inicial vacío
        reconstructed = {}
        for path, value in entries:
            keys = parse_path(path)  # Convertimos la ruta en una lista de claves
            set_nested_value(reconstructed, keys, value)  # Insertamos el valor en la estructura

        return reconstructed

    def get_content_json_file(self, file_path: str or Path = None) -> Union[Dict, List]:
        """
        Carga el contenido de un archivo JSON y lo convierte en un diccionario o lista de Python.

        :param file_path: Ruta del archivo JSON (si no se proporciona, se utiliza self.file_path).
        :return: Diccionario o lista con los datos cargados.
        """
        file_path = file_path or self.file_path
        if not file_path:
            raise ValueError("No se proporcionó una ruta de archivo JSON.")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data
        except Exception as e:
            log.error(f"Error al cargar el archivo JSON: {e}")
            raise

    def save_json_file(self, data: Union[Dict, List], file_path: str = None):
        """
        Guarda  datos como archivo JSON.

        :param data: Diccionario o lista con los datos a guardar.
        :param file_path: Ruta del archivo JSON (si no se proporciona, se utiliza self.file_path).
        """
        file_path = file_path or self.file_path
        if not file_path:
            raise ValueError("No se proporcionó una ruta de archivo JSON.")

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            log.warning(f"El archivo JSON se guardó correctamente en '{file_path}'.")
        except Exception as e:
            log.error(f"Error al guardar el archivo JSON: {e}")
            raise


# Ejemplo de uso de la clase GestionarJSON
# if __name__ == "__main__":
#     gestor_json = JSON(r"/struct_files\en.json")
#
#     # Cargar datos desde un archivo JSON
#     datos = gestor_json.get_content_json_file()
#     log.info("Data:         ", datos)
#     serializer_json = gestor_json.serializer_json(datos)
#     log.info("Serializar:   ", serializer_json)
#     deserializer_json = JSON.deserializar_json(serializer_json)
#     log.info("Deserializado:", deserializer_json)
