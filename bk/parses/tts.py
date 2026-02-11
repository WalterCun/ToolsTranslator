#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" bk/parses/i18n_ts.py """
import re
import json
import logging
from pathlib import Path
from typing import Dict, Optional

log = logging.getLogger(__name__)

class TypeScriptI18n:
    """
    Clase para gestionar archivos de internacionalización (i18n) en formato TypeScript.
    Incluye funciones para extraer, convertir y manipular datos de archivos i18n.ts.
    """
    
    # Patrón para extraer el objeto de mensajes del archivo i18n.ts
    PATTERN_I18N = re.compile(
        r"const\s+messages\s*=\s*"  # busca 'const messages ='
        r"(\{[\s\S]*?\})"  # captura desde la primera '{' hasta el último '}'
        r"\s*export\s+default",  # asegura que es el bloque que sigue al export
        re.MULTILINE
    )
    
    def __init__(self, file_path: str = None):
        """
        Constructor para inicializar un objeto de gestión de archivos i18n.ts.
        
        :param file_path: Ruta del archivo i18n.ts (opcional).
        """
        self.file_path = file_path
    
    def extract_messages(self, content: str) -> Optional[str]:
        """
        Extrae el objeto de mensajes de un archivo i18n.ts.
        
        :param content: Contenido del archivo i18n.ts.
        :return: Cadena con el objeto de mensajes o None si no se encuentra.
        """
        match = self.PATTERN_I18N.search(content)
        if match:
            return match.group(1)
        return None
    
    @staticmethod
    def ts_to_dict(ts_content: str) -> Dict:
        """
        Convierte un objeto JavaScript/TypeScript a un diccionario de Python.
        
        :param ts_content: Contenido del objeto JavaScript/TypeScript.
        :return: Diccionario de Python equivalente.
        """
        # Preparar el contenido para ser interpretado como JSON
        # 1. Reemplazar comillas simples por comillas dobles
        json_like = ts_content.replace("'", '"')
        
        # 2. Asegurar que todas las claves tengan comillas dobles
        # Buscar patrones como {key: value, o {key:{
        json_like = re.sub(r'(\{|\,)\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', json_like)
        
        # 3. Manejar casos especiales como caracteres de escape
        json_like = json_like.replace('\\"', '"').replace('\\"', '"')
        
        try:
            # Intentar cargar como JSON
            return json.loads(json_like)
        except json.JSONDecodeError as e:
            log.error(f"Error al convertir TypeScript a diccionario: {e}")
            log.error(f"Error en la posición: {e.pos}")
            
            # Contar líneas manualmente para el error
            newline_count = 0
            for i in range(e.pos):
                if json_like[i] == '\n':
                    newline_count += 1
            log.error(f"Línea: {newline_count + 1}")
            
            # Si falla el primer intents, probar con un enfoque manual más robusto
            try:
                # Reemplazar todas las claves sin comillas con comillas
                manual_json = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', ts_content)
                # Reemplazar comillas simples con comillas dobles
                manual_json = manual_json.replace("'", '"')
                # Eliminar comas finales en objetos y arrays
                manual_json = re.sub(r',\s*}', '}', manual_json)
                manual_json = re.sub(r',\s*]', ']', manual_json)
                
                return json.loads(manual_json)
            except Exception as e2:
                log.error(f"Error con enfoque manual: {e2}")
                # Si todo falla, devolver un diccionario vacío
                return {}
    
    def get_content_from_file(self, file_path: str = None) -> Dict:
        """
        Lee un archivo i18n.ts y extrae su contenido como un diccionario de Python.
        
        :param file_path: Ruta del archivo i18n.ts (si no se proporciona, se utiliza self.file_path).
        :return: Diccionario con los datos extraídos.
        """
        file_path = file_path or self.file_path
        if not file_path:
            raise ValueError("No se proporcionó una ruta de archivo i18n.ts.")
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            # Extraer el objeto de mensajes
            messages_obj = self.extract_messages(content)
            if not messages_obj:
                raise ValueError("No se pudo extraer el objeto de mensajes del archivo i18n.ts.")
            
            # Convertir a diccionario de Python
            return self.ts_to_dict(messages_obj)
        except Exception as e:
            log.error(f"Error al procesar el archivo i18n.ts: {e}")
            raise
    
    def save_as_json(self, output_path: str, data: Dict = None):
        """
        Guarda los datos extraídos como un archivo JSON.
        
        :param output_path: Ruta donde guardar el archivo JSON.
        :param data: Datos a guardar (si no se proporciona, se extraen del archivo configurado).
        """
        if data is None:
            data = self.get_content_from_file()
        
        try:
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            log.info(f"Archivo JSON guardado correctamente en '{output_path}'.")
        except Exception as e:
            log.error(f"Error al guardar el archivo JSON: {e}")
            raise
    
    def save_languages_separately(self, output_dir: str, data: Dict = None):
        """
        Guarda cada idioma del archivo i18n.ts como un archivo JSON separado.
        
        :param output_dir: Directorio donde guardar los archivos JSON.
        :param data: Datos a guardar (si no se proporciona, se extraen del archivo configurado).
        :return: Lista de rutas de los archivos guardados.
        """
        if data is None:
            data = self.get_content_from_file()
        
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(exist_ok=True, parents=True)
        
        saved_files = []
        
        for lang, lang_data in data.items():
            output_file = output_dir_path / f"{lang}.json"
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(lang_data, f, indent=4, ensure_ascii=False)
                log.info(f"Archivo JSON para el idioma '{lang}' guardado en '{output_file}'.")
                saved_files.append(str(output_file))
            except Exception as e:
                log.error(f"Error al guardar el archivo JSON para el idioma '{lang}': {e}")
        
        return saved_files


# Ejemplo de uso
if __name__ == "__main__":
    ts_parser = TypeScriptI18n("D:\Coders\ToolsTranslator\struct_files\i18n.ts")
    data = ts_parser.get_content_from_file()
    print(data)
    
    # Guardar como JSON
    # ts_parser.save_as_json("struct_files/output/i18n_all.json")
    
    # Guardar cada idioma por separado
    # ts_parser.save_languages_separately("struct_files/output")