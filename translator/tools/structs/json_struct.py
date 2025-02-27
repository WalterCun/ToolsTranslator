import json
import logging
from typing import Any, Dict, List, Tuple, Union

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

__all__ = ['json_extract_entries']

def json_extract_entries(data: Union[Dict, List], path="") -> List[Tuple[str, str]]:
    """
    Extrae todas las entradas de texto de un JSON estructurado.

    :param data: Diccionario o lista con estructura i18n.
    :param path: Ruta actual dentro de la estructura.
    :return: Lista de tuplas con (ruta, texto).
    """
    text_entries = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            text_entries.extend(json_extract_entries(value, new_path))

    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_path = f"{path}[{index}]"
            text_entries.extend(json_extract_entries(item, new_path))

    elif isinstance(data, str):
        text_entries.append((path, data))

    return text_entries


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Carga un archivo JSON y devuelve su contenido como un diccionario.

    :param file_path: Ruta del archivo JSON.
    :return: Diccionario con la estructura del JSON.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error al cargar el archivo JSON: {e}")
        return {}


if __name__ == "__main__":
    # Prueba con un archivo JSON
    json_file = "example.json"
    json_data = load_json_file(json_file)

    if json_data:
        extracted_texts = json_extract_entries(json_data)
        for path, text in extracted_texts:
            print(f"Ruta: {path} -> {text}")
