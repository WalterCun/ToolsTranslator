# Uso como Librería — API Detallada

## Inicialización

```python
from translator import Translator

trans = Translator(
    lang="es",                      # Idioma activo inicial
    directory="./locales",          # Directorio de archivos de idioma
    auto_add_missing_keys=False,    # Agregar claves faltantes automáticamente
    missing_key_behavior="key",     # "key" o "message"
    fallback_lang=None,             # None=auto(lang), ""=deshabilitado, "xx"=explícito
    base_url="http://localhost:5000",  # URL de LibreTranslate
    timeout=10.0,                   # Timeout HTTP en segundos
    adapter=None,                   # Adapter personalizado (opcional)
)
```

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `lang` | `str` | `"en"` | Idioma activo inicial |
| `directory` | `str\|Path` | `"./locales"` | Directorio de archivos de idioma |
| `auto_add_missing_keys` | `bool` | `False` | Agregar claves faltantes al archivo |
| `missing_key_behavior` | `str` | `"key"` | Qué retornar: `"key"` o `"message"` |
| `fallback_lang` | `str\|None` | `None` | Idioma fallback (None=auto, ""=off) |
| `missing_value_template` | `str` | `"TODO: agregar traducción"` | Valor para claves auto-agregadas |
| `base_url` | `str` | `"http://localhost:5000"` | URL de LibreTranslate |
| `timeout` | `float` | `10.0` | Timeout HTTP |
| `adapter` | `TranslationAdapter` | `None` | Adapter custom (reemplaza base_url/timeout) |

## Acceso a Traducciones

### Por atributos (recomendado)

```python
# Archivo: locales/es.json
# {"app": {"title": "Mi App", "buttons": {"save": "Guardar"}}}

trans = Translator(lang="es", directory="./locales")

trans.app.title          # "Mi App"
trans.app.buttons.save   # "Guardar"
```

### Por clave con puntos

```python
trans.get("app.title")              # "Mi App"
trans.get("app.buttons.save")       # "Guardar"
trans.get("missing", default="N/A") # "N/A" (no existe)
```

### Acceso cruzado a idiomas

```python
trans.get("app.title", lang="en")  # Busca en en.json sin cambiar el idioma activo
```

## Gestión de Idioma

### Cambiar idioma activo

```python
trans.change_lang("en")  # Método
trans.lang = "fr"         # Property
```

### Listar idiomas disponibles

```python
trans.available_languages()  # ["en", "es", "fr"]
```

### Idioma fallback

```python
# Fallback automático (default): si "fr" no existe, usa "en"
trans = Translator(lang="en", directory=dir, fallback_lang=None)

# Fallback explícito
trans = Translator(lang="en", directory=dir, fallback_lang="es")

# Sin fallback: lanza error si el idioma no existe
trans = Translator(lang="en", directory=dir, fallback_lang="")
```

## Traducción Remota

### Texto directo

```python
# Síncrono
result = trans.translate("Hello", source="en", target="es")  # "Hola"

# Async
result = await trans.translate_async("Hello", source="en", target="es")
```

### Con fallback

```python
# String como fallback
result = trans.translate("Hello", fallback="Error")

# Función como fallback
result = trans.translate("Hello", fallback=lambda t: f"[{t}]")
```

### Valores dinámicos en archivos

```json
{
  "greeting": {
    "__translate__": "Hello",
    "source": "en",
    "target": "es"
  }
}
```

```python
trans.get("greeting")  # Ejecuta translate("Hello", source="en", target="es")
```

## Claves Faltantes

### Auto-agregar

```python
trans = Translator(lang="es", directory=dir, auto_add_missing_keys=True)
trans.get("new.key")  # Agrega "new.key" al archivo con valor "TODO: agregar traducción"
```

### Comportamiento personalizado

```python
# Retornar la clave misma
trans = Translator(lang="es", directory=dir, missing_key_behavior="key")
trans.get("missing")  # "missing"

# Retornar mensaje
trans = Translator(lang="es", directory=dir, missing_key_behavior="message")
trans.get("missing")  # "Missing translation"

# Con default explícito (prioridad más alta)
trans.get("missing", default="Mi default")  # "Mi default"
```

## Generación de Archivos

### Generar un idioma

```python
result = trans.generate_language_file(
    base_file="locales/en.json",
    target_lang="fr",
    output="locales/fr.json",
    source_lang="en",
    mark_pending=True  # Marca fallos como "__PENDING__:texto"
)
# result = {"greeting": "Bonjour", "button": "Entrer", ...}
```

### AutoTranslate (múltiples idiomas)

```python
from translator.core.autotranslate import AutoTranslate, AutoTranslateOptions
from translator.utils.fileinfo import TranslateFile

options = AutoTranslateOptions(
    langs=["es", "fr", "de"],
    overwrite=True
)
file_info = TranslateFile("locales/en.json")

auto = AutoTranslate(file_info, options, adapter=mi_adapter)
result = auto.worker()

print(f"Generados: {result.generated_files}")
print(f"Traducidos: {result.translated_keys}")
print(f"Fallidos: {result.failed_keys}")
```

### Conversión de formato

```python
trans.convert_json_to_yaml("locales/en.json", "locales/en.yaml")
trans.convert_yaml_to_json("locales/en.yaml", "locales/en.json")
```

## Adapter Personalizado

### Implementación básica

```python
from translator import Translator, TranslationAdapter

class GoogleTranslateAdapter:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def available(self) -> tuple[bool, str]:
        return True, "ok"

    def translate(self, text: str, source: str, target: str) -> str:
        # Tu lógica de traducción
        return translated_text

trans = Translator(lang="es", adapter=GoogleTranslateAdapter("mi-key"))
```

### Con cache

```python
class CachedAdapter:
    def __init__(self, inner: TranslationAdapter):
        self._inner = inner
        self._cache = {}

    def available(self) -> tuple[bool, str]:
        return self._inner.available()

    def translate(self, text: str, source: str, target: str) -> str:
        key = (text, source, target)
        if key not in self._cache:
            self._cache[key] = self._inner.translate(text, source, target)
        return self._cache[key]
```

## Thread Safety

`Translator` es thread-safe para lecturas concurrentes. Para escrituras (`auto_add_missing_keys`), usa un lock interno.

```python
import threading

trans = Translator(lang="es", directory=dir, auto_add_missing_keys=True)

def worker(idx):
    trans.get(f"key_{idx}")  # Seguro desde múltiples threads

threads = [threading.Thread(target=worker, args=(i,)) for i in range(100)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Cache

### Resolved cache
Los resultados de `get()` y `resolve_attr` se cachean internamente. Se invalida al cambiar de idioma.

### Server availability cache
`LibreTranslateClient.available()` tiene un TTL de 30 segundos. Las llamadas repetidas a `translate()` no verifican el servidor cada vez.

## Excepciones

```python
from translator.exceptions import (
    ToolsTranslatorError,          # Base
    ServiceUnavailableError,       # Servicio caído
    ExtraNotInstalledError,        # Falta dependencia opcional
    TranslationFileError,          # Archivo corrupto
    LanguageNotAvailableError,     # Idioma no existe
)
```
