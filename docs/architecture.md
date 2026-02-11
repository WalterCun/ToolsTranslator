# Arquitectura

ToolsTranslator está diseñado con una arquitectura modular que separa claramente las responsabilidades de gestión de archivos, traducción y acceso a datos.

## Estructura del Proyecto

El proyecto se organiza en los siguientes módulos principales:

- **`translator/core`**: Contiene la lógica central de la librería.
    - `Translator`: Clase principal que actúa como punto de entrada para el usuario. Gestiona la carga de archivos, el acceso a claves y la interacción con adaptadores de traducción.
    - `AutoTranslate`: Componente opcional para la generación automática de archivos de idioma utilizando servicios externos.

- **`translator/adapters`**: Define interfaces y adaptadores para servicios de traducción.
    - `TranslationAdapter`: Protocolo que define la interfaz común para cualquier servicio de traducción.
    - `LibreTranslateClient`: Implementación concreta para interactuar con la API de LibreTranslate.

- **`translator/handlers`**: Manejadores de formatos de archivo.
    - `JsonHandler`: Lectura y escritura de archivos JSON.
    - `YamlHandler`: Lectura y escritura de archivos YAML (requiere `PyYAML`).

- **`translator/cli`**: Interfaz de línea de comandos (CLI) construida con `Typer`.
    - `app.py`: Definición de comandos (`install`, `doctor`, `status`, etc.) para gestionar el servidor de traducción local.
    - `DockerManager`: Utilidad para interactuar con Docker y gestionar el contenedor de LibreTranslate.

- **`translator/utils`**: Utilidades generales.
    - `fileinfo.py`: Clases auxiliares para manejar información de archivos (`TranslateFile`).

## Separación de Responsabilidades

### Modo Archivos (Estático)

En su uso más básico, `Translator` opera en modo "archivos". Carga los datos de traducción desde archivos JSON o YAML en memoria y permite acceder a ellos mediante atributos dinámicos (`__getattr__`).

- **Ventajas**: Rápido, sin dependencias externas en tiempo de ejecución, ideal para producción.
- **Flujo**: `Translator` -> `JsonHandler`/`YamlHandler` -> Archivos locales.

### Modo Server (Dinámico/Opcional)

Para funcionalidades avanzadas como `AutoTranslate` o traducción en tiempo real (`translate()`), `Translator` puede utilizar un adaptador de traducción.

- **Requisitos**: Requiere instalar las dependencias extra `[server]` y tener acceso a un servidor LibreTranslate (local o remoto).
- **Flujo**: `Translator` -> `LibreTranslateClient` -> API HTTP -> Servidor LibreTranslate.

## Extensibilidad

La arquitectura permite extender la funcionalidad mediante:

1.  **Nuevos Adaptadores**: Implementando `TranslationAdapter` para soportar otros servicios de traducción (ej. Google Translate, DeepL).
2.  **Nuevos Formatos**: Añadiendo manejadores en `translator/handlers` para soportar otros formatos de archivo (ej. TOML, XML).
