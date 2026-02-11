# Extensibilidad

ToolsTranslator está diseñado para ser flexible y extensible. Puedes añadir soporte para nuevos formatos de archivo o integrar servicios de traducción adicionales.

## Añadir Nuevos Formatos

Para soportar un nuevo formato de archivo (ej. TOML), debes crear un manejador que implemente los métodos `read` y `write`.

1.  Crea una clase `TomlHandler` en `translator/handlers/toml_handler.py`.
2.  Implementa la lógica de lectura y escritura utilizando una librería como `toml`.
3.  Registra el manejador en `Translator._read_file` y `Translator._write_file`.

```python
# translator/handlers/toml_handler.py
import toml
from pathlib import Path
from typing import Any

class TomlHandler:
    @staticmethod
    def read(path: Path) -> dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return toml.load(f)

    @staticmethod
    def write(path: Path, data: dict[str, Any]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            toml.dump(data, f)
```

## Integrar Nuevos Backends de Traducción

Si deseas utilizar un servicio de traducción diferente a LibreTranslate (ej. Google Translate API), puedes crear un adaptador personalizado.

1.  Crea una clase que implemente el protocolo `TranslationAdapter`.
2.  Define los métodos `available` y `translate`.
3.  Pasa tu adaptador al constructor de `AutoTranslate` o configúralo en `Translator`.

```python
# translator/adapters/google_translate.py
from translator.adapters.libretranslate import TranslationAdapter

class GoogleTranslateAdapter(TranslationAdapter):
    def available(self) -> tuple[bool, str]:
        # Lógica para verificar disponibilidad de la API
        return True, "ok"

    def translate(self, text: str, source: str, target: str) -> str:
        # Lógica para llamar a la API de Google Translate
        return "Translated text"
```

## Uso con AutoTranslate

```python
from translator.core.autotranslate import AutoTranslate
from translator.adapters.google_translate import GoogleTranslateAdapter

adapter = GoogleTranslateAdapter()
auto = AutoTranslate(..., adapter=adapter)
```
