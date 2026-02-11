# ToolsTranslator

Librería Python publicable en PyPI para:

- Proxy de traducción contra LibreTranslate.
- Gestión de archivos de idioma (`.json`) con soporte opcional YAML.
- Proxy dinámico de traducciones por atributos (`__getattr__`).
- Generación automática de archivos de idioma desde un idioma base.
- CLI opcional para instalar/diagnosticar LibreTranslate en Docker.

## Instalación

### Básica (modo proxy)

```bash
pip install toolstranslator
```

### Extra YAML

```bash
pip install toolstranslator[yml]
```

### Extra Server (CLI)

```bash
pip install toolstranslator[server]
```

## API principal

```python
from toolstranslator import Translator

trans = Translator(
    lang="es",
    directory="./locales",
    auto_add_missing_keys=True,
)
```

## Idioma por defecto + cambio en caliente

```python
trans = Translator(lang="es")
trans.lang = "en"           # recarga sin reiniciar instancia
trans.change_lang("fr")     # alternativa explícita
```

## Proxy por atributos dinámicos

```python
# es.json -> {"hola": "mundo", "bienvenida": {"usuario": "Hola"}}

str(trans.hola)                # "mundo"
str(trans.bienvenida.usuario)  # "Hola"
```

## auto_add_missing_keys

```python
trans = Translator(lang="es", auto_add_missing_keys=True)
str(trans.app.header.title)  # crea clave faltante en archivo de idioma
```

- `True`: crea clave con valor `"TODO: agregar traducción"`.
- `False`: no escribe archivo y devuelve el nombre de la clave.
- Se puede cambiar en caliente:

```python
trans.auto_add_missing_keys = False
```

## Uso como proxy remoto

```python
translated = trans.translate("Hola mundo", source="es", target="en")
```

Fallback cuando LibreTranslate no está disponible:

```python
translated = trans.translate(
    "Hola mundo",
    source="es",
    target="en",
    fallback=lambda text: f"[pending]{text}",
)
```

## Generación de idiomas

```python
trans.generate_language_file(
    base_file="./locales/es.json",
    target_lang="en",
    output="./locales/en.json",
    source_lang="es",
    mark_pending=True,
)
```

## CLI (extra `server`)

```bash
toolstranslator install
toolstranslator doctor
```

## Desde Git

```bash
pip install git+https://github.com/usuario/toolstranslator
```

## Documentación

- `docs/architecture.md`
- `docs/installation.md`
- `docs/usage.md`
- `docs/cli.md`
- `docs/extensibility.md`
