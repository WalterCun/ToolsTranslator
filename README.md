# translation-tools

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

Librería y CLI para traducir archivos i18n y gestionar traducciones locales utilizando un servicio LibreTranslate.

- Requiere Python 3.10+
- Recomendado tener LibreTranslate disponible en http://localhost:5000 (ver docs/HOWTO_DOCKER.md)

## Características

- Librería y CLI para gestionar traducciones por idioma en archivos JSON.
- Integración con LibreTranslate (http://localhost:5000 por defecto) con cache y reintentos.
- Detección automática de idioma base al traducir archivos.
- Soporte de formatos para AutoTranslate: JSON; YAML/YML en desarrollo (instalar el extra `yml` para parseo).
- Utilidades para i18n.ts (TypeScript) de forma experimental (ver translator/parses/tts.py).
- Herramientas para validar/levantar el servicio con Docker cuando es posible.

## Requisitos

- Python 3.10 o superior.
- Servicio LibreTranslate accesible en http://localhost:5000.
  - Si no tienes uno, revisa docs/HOWTO_DOCKER.md para iniciarlo automáticamente vía Docker.

## Instalación

```powershell
pip install translation-tools
# Soporte YAML (opcional)
pip install "translation-tools[yml]"
```

## Formatos soportados

- JSON: Soportado plenamente para librería y AutoTranslate.
- YAML/YML: Requiere instalar el extra `yml` (pyyaml).
- TypeScript (i18n.ts): utilidades de parseo disponibles, AutoTranslate aún no soporta TS directamente.

## Uso rápido (librería)

```python
from pathlib import Path
from translator import Translator

langs_dir = Path("./langs")
tr = Translator(translations_dir=langs_dir, default_lang="en")

# Agrega una traducción al archivo de español
tr.add_trans(key="greeting", lang="es", value="Hola mundo")

# Cambia el idioma activo y lee la clave como atributo
tr.lang = "es"
print(tr.greeting)  # Si no existe, se guardará "No implement Translation" y se devolverá ese texto
```

### Uso avanzado (librería)

```python
from pathlib import Path
from translator import Translator

# Inicializar el traductor
tr = Translator(translations_dir=Path("./langs"), default_lang="en")

# Cambiar dinámicamente el idioma
tr.lang = "fr"
print(tr.greeting)

# Idiomas soportados por el servicio
print(tr.api.get_supported_languages("en", to_list=True))
```

## AutoTranslate (librería)

Traduce un archivo base (JSON/YAML) a otros idiomas.

```python
from pathlib import Path
from translator.core.autotranslate import AutoTranslate
from translator.utils import TranslateFile

src = Path("./struct_files/en.json")
info = TranslateFile(src)
auto = AutoTranslate(info)
# Traduce a los idiomas soportados (o configura idiomas en el CLI)
auto.worker()
```

## Uso rápido (CLI)

- Versión
```powershell
python -m translator --version
```

- Agregar una traducción
```powershell
# Crear o actualizar ./langs/es.json con una nueva clave
python -m translator add .\langs\es.json --key greeting --lang es "Hola mundo"
```

- Traducción automática de archivos
```powershell
# Traducir un archivo base a varios idiomas
python -m translator auto-translate .\struct_files\en.json --langs es fr

# Directorio de salida y sobreescritura
python -m translator auto-translate .\struct_files\en.json --langs es fr --output .\struct_files\output --overwrite
```

Parámetros principales de auto-translate:
- --base: Idioma base si no se detecta desde el nombre del archivo.
- --langs: Idiomas destino (ej. es en fr). Acepta múltiples valores o "all".
- --output: Directorio donde escribir las salidas JSON.
- --force: Forzar traducciones aunque ya existan.
- --overwrite: Incluir el idioma base cuando se usa "all" y sobreescribir salidas.

## Servicio LibreTranslate y Docker

- Por defecto se usa http://localhost:5000. La herramienta intentará validar e iniciar un contenedor "libretranslate" usando Docker cuando sea posible.
- En entornos no interactivos (CI) o sin Docker, asegúrate de tener el servicio corriendo previamente.
- Más detalles en [docs/HOWTO_DOCKER.md](docs/HOWTO_DOCKER.md).

## Documentación

- Guía de uso: [docs/USAGE.md](docs/USAGE.md)
- Referencia de API: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- LibreTranslate + Docker: [docs/HOWTO_DOCKER.md](docs/HOWTO_DOCKER.md)
- Desarrollo/Instalación: [docs/INSTALL_DEV.md](docs/INSTALL_DEV.md)
- Arquitectura: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Ejemplos ejecutables

- examples/simple_translator.py
- examples/auto_translate_file.py
- examples/check_service.py

## Contribuir

Las contribuciones son bienvenidas. Revisa [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

## Soporte y issues

Reporta problemas o solicita mejoras en: https://github.com/WalterCun/ToolsTranslator/issues

## Licencia

Este proyecto está disponible bajo la [Licencia MIT](LICENSE).