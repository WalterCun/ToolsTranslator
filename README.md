# ToolsTranslator

Librería Python publicable en PyPI para:

- Proxy de traducción contra LibreTranslate.
- Gestión de archivos de idioma (`.json`) con soporte opcional YAML.
- Generación automática de archivos de idioma desde un idioma base.
- CLI opcional para instalar/diagnosticar LibreTranslate en Docker.

## Instalación

### Básica (modo proxy)

```bash
pip install toolstranslator
```

Incluye solo SDK base (proxy HTTP + utilidades JSON).

### Extra YAML

```bash
pip install toolstranslator[yml]
```

Habilita lectura/escritura YAML y conversiones JSON↔YAML.

### Extra Server

```bash
pip install toolstranslator[server]
```

Habilita comandos CLI:

- `toolstranslator install`
- `toolstranslator doctor`

## Uso como proxy

```python
from toolstranslator import Translator

t = Translator()
print(t.translate("Hola mundo", source="es", target="en"))
```

### Fallback cuando no está LibreTranslate

```python
from toolstranslator import Translator

t = Translator()
translated = t.translate(
    "Hola mundo",
    source="es",
    target="en",
    fallback=lambda text: f"[pending]{text}"
)
```

## Uso con archivos

```python
from toolstranslator import Translator

translator = Translator(directory="./locales")
value = translator.get("home.title", lang="es")  # si no existe devuelve la clave
```

## Generación de idiomas

```python
from toolstranslator import Translator

Translator().generate_language_file(
    base_file="./locales/es.json",
    target_lang="en",
    output="./locales/en.json",
    source_lang="es",
    mark_pending=True,
)
```

## CLI

```bash
toolstranslator install
toolstranslator doctor
```

## Integración en otros proyectos

También puede instalarse desde Git:

```bash
pip install git+https://github.com/usuario/toolstranslator
```

## Documentación

- `docs/architecture.md`
- `docs/installation.md`
- `docs/usage.md`
- `docs/cli.md`
- `docs/extensibility.md`
