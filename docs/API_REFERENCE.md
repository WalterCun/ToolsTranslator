# Referencia de API

Esta referencia resume las clases y funciones públicas más importantes del paquete translation-tools. Consulte las docstrings en el código para detalles completos.

- Módulo: translator.core.translate
  - Clase: Translator
    - propósito: Manejo de traducciones basadas en archivos JSON por idioma.
    - __init__(translations_dir: Path = BASE_DIR/"langs", default_lang: str = "en")
    - prop lang: str — idioma actual (getter/setter valida contra idiomas soportados).
    - add_trans(key: str, lang: str, value: str, force: bool = False) -> None — agrega/actualiza una traducción.
    - Acceso dinámico a claves: tr.<clave> devuelve la traducción o guarda "No implement Translation".

- Módulo: translator.core.autotranslate
  - Clase: AutoTranslate
    - propósito: Traducir archivos completos (JSON o i18n.ts) a uno o varios idiomas.
    - __init__(file_translation: TranslateFile, args: argparse.Namespace = Namespace(base=None))
      - args esperados: base (str), langs (list[str] | str), output (Path), force (bool), overwrite (bool)
    - worker(base: str | None = None, langs: list[str] | str | None = None) -> None — orquesta el proceso de traducción.

- Módulo: translator.utils.extract_info_file
  - Función: extract_first_primitive_value(data) -> Any — extrae el primer valor primitivo de estructuras anidadas.
  - Clase: TranslateFile
    - propósito: Leer y normalizar contenido desde archivos de traducciones.
    - Atributos de solo lectura: path, directory, file, name, ext, content.

- Módulo: translator.api.translate_api
  - Clase: LibreTranslate
    - propósito: Encapsula llamadas al servicio LibreTranslate (HTTP).
    - Métodos principales:
      - get_supported_languages(lang_base: str, to_list: bool = False) -> list|dict
      - detect_language(text: str) -> tuple[str, float] | ("No detect a language", None)
      - translate(text: str, source: str|None, target: str, retry: int = 0) -> str

- CLI: python -m translator
  - Comando: add
    - Uso: python -m translator add <ruta_json> --key <clave> --lang <codigo> "valor"
  - Comando: auto-translate
    - Uso: python -m translator auto-translate <archivo_base.json> --langs es fr [--output .\salida] [--force] [--overwrite] [--base en]

Notas importantes

- LibreTranslate debe estar accesible en http://localhost:5000. El paquete incluye validadores para iniciar el servicio mediante Docker si es posible (ver docs/HOWTO_DOCKER.md).
- Para YAML, instale extra yml: pip install "translation-tools[yml]".