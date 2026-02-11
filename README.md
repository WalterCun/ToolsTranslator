# ToolsTranslator

Librería Python para la gestión de traducciones y archivos de idioma en aplicaciones, con soporte opcional para traducción automática mediante LibreTranslate.

## Características principales

- **Gestión de archivos de idioma**: Carga y gestión de archivos `.json` (y opcionalmente `.yaml`/`.yml`).
- **Acceso dinámico**: Acceso a claves de traducción mediante atributos (`trans.home.title`).
- **Traducción automática**: Generación de archivos de idioma faltantes utilizando un servidor LibreTranslate.
- **Modo Proxy**: Traducción de textos en tiempo real.
- **CLI**: Herramientas de línea de comandos para gestionar el servidor de traducción (Docker).

## Instalación

### Básica (solo gestión de archivos)

```bash
pip install toolstranslator
```

### Con soporte YAML

```bash
pip install toolstranslator[yml]
```

### Con soporte para Servidor (CLI y Docker)

```bash
pip install toolstranslator[server]
```

## Uso Básico

### Inicialización

```python
from translator import Translator

# Inicializa el traductor apuntando a tu directorio de locales
trans = Translator(
    lang="es",
    directory="./locales",
    auto_add_missing_keys=True  # Crea claves faltantes automáticamente en el archivo
)
```

### Acceso a traducciones

Supongamos que tienes un archivo `locales/es.json`:
```json
{
  "home": {
    "title": "Bienvenido",
    "button": "Entrar"
  }
}
```

Puedes acceder a las traducciones así:

```python
print(trans.home.title)  # Salida: Bienvenido
print(trans.get("home.button")) # Salida: Entrar
```

### Cambio de idioma

```python
trans.change_lang("en")
# O mediante la propiedad
trans.lang = "fr"
```

### Manejo de claves faltantes

Si `auto_add_missing_keys=True`, al acceder a una clave que no existe, se añadirá al archivo del idioma actual con un valor por defecto ("TODO: agregar traducción").

```python
print(trans.new.key) # Escribe "new.key" en el archivo y devuelve el placeholder
```

## Funcionalidades Avanzadas

### AutoTranslate (Generación de archivos)

Esta funcionalidad permite generar archivos de traducción para nuevos idiomas basándose en un archivo existente. Requiere el extra `server` o un adaptador configurado.

*Nota: Esta funcionalidad está diseñada para ser usada programáticamente o mediante scripts específicos, separada del flujo principal de la aplicación.*

```python
from translator.core.autotranslate import AutoTranslate, AutoTranslateOptions
from translator.utils.fileinfo import TranslateFile

# Configuración
options = AutoTranslateOptions(
    langs=["en", "fr"],
    overwrite=False
)
file_info = TranslateFile("locales/es.json")

# Ejecución (requiere servidor LibreTranslate activo si use_server=True)
auto = AutoTranslate(file_info, options, use_server=True)
result = auto.worker()

print(f"Archivos generados: {result.generated_files}")
```

### CLI (Gestión del Servidor)

Si instalaste con `[server]`, tienes acceso al comando `toolstranslator` para gestionar una instancia local de LibreTranslate usando Docker.

```bash
# Verificar estado del entorno
toolstranslator doctor

# Instalar y arrancar el servidor
toolstranslator install

# Ver estado
toolstranslator status

# Reiniciar servidor
toolstranslator restart
```

## Estructura del Proyecto

El proyecto se divide en:

- `translator/core`: Lógica principal (`Translator`, `AutoTranslate`).
- `translator/adapters`: Adaptadores para servicios externos (LibreTranslate).
- `translator/handlers`: Manejadores de formatos de archivo (JSON, YAML).
- `translator/cli`: Interfaz de línea de comandos.

## Documentación Adicional

Consulta el directorio `docs/` para más detalles:

- [Arquitectura](docs/architecture.md)
- [Instalación](docs/installation.md)
- [Uso](docs/usage.md)
- [CLI](docs/cli.md)
- [AutoTranslate](docs/autotranslate.md)
