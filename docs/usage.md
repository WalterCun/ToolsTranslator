# Guía de Uso

Esta guía explica cómo instalar y utilizar el paquete translation-tools para traducir archivos i18n o realizar traducciones simples utilizando un servicio LibreTranslate local.

Importante: Este paquete asume que existe un servicio LibreTranslate accesible en http://localhost:5000. Incluye utilidades para validar e iniciar el servicio mediante Docker cuando es posible.

- Requisitos
  - Python >= 3.10
  - Docker Desktop/Engine instalado si desea iniciar LibreTranslate automáticamente mediante Docker.

Instalación

- pip install translation-tools

Uso rápido (librería)

Ejemplo mínimo de uso programático. Nota: Al crear Translator se verificará/iniciará el servicio de LibreTranslate si es necesario.

```python
from pathlib import Path
from bk import Translator

# Directorio donde se guardarán/leerán las traducciones en JSON
langs_dir = Path("./langs")

# Crear el traductor con idioma por defecto en inglés
tr = Translator(translations_dir=langs_dir, default_lang="en")

# Agregar una traducción manualmente al archivo en español (./langs/es.json)
tr.add_trans(key="greeting", lang="es", value="Hola mundo")

# Acceder a una clave como atributo (buscará en el idioma actual)
print(tr.greeting)  # Si no existe, guardará "No implement Translation" y lo devolverá
```

Uso rápido (CLI)

El paquete expone un CLI basado en `python -m translator` con dos subcomandos: `add` y `auto-translate`.

- Agregar una traducción

```powershell
# Crea o actualiza ./langs/es.json agregando la clave "greeting"
python -m translator add .\langs\es.json --key greeting --lang es "Hola mundo"
```

- Traducir automáticamente un archivo base a otros idiomas

```powershell
# Traduce struct_files\en.json a los idiomas español y francés y escribe en el mismo directorio
python -m translator auto-translate .\struct_files\en.json --langs es fr

# Opcionalmente puedes indicar un directorio de salida y sobrescribir
python -m translator auto-translate .\struct_files\en.json --langs es fr --output .\struct_files\output --overwrite
```

AutoTranslate (API)

Para traducir un archivo desde código, utiliza AutoTranslate y TranslateFile:

```python
from pathlib import Path
from bk.core.autotranslate import AutoTranslate
from bk.utils import TranslateFile

src = Path("./struct_files/en.json")
info = TranslateFile(src)
auto = AutoTranslate(info)
# Traduce a todos los idiomas soportados (o usa --langs desde CLI)
auto.worker()
```

Notas sobre LibreTranslate y Docker

- El paquete intentará detectar si Docker está instalado y corriendo. Si no, solicitará confirmación para instalar/iniciar (funcionalidad orientada a entornos de desarrollo). En servidores CI o entornos sin Docker, asegúrate de disponer del servicio libretranslate accesible en http://localhost:5000.
- También puedes gestionar el servicio con las herramientas provistas. Consulta docs/HOWTO_DOCKER.md.

Convenciones de archivos

- El traductor por defecto utiliza archivos JSON por idioma con nombre {lang}.json dentro del directorio configurado (por defecto ./langs).