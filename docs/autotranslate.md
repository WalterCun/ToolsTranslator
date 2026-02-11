# AutoTranslate

La funcionalidad `AutoTranslate` permite generar archivos de traducción para nuevos idiomas basándose en un archivo existente, utilizando un servicio de traducción externo (como LibreTranslate).

## ¿Qué es AutoTranslate?

Es una herramienta avanzada que automatiza el proceso de traducción de textos. En lugar de traducir manualmente cada clave de un archivo JSON/YAML, `AutoTranslate` recorre el archivo base, detecta las claves faltantes en el idioma destino y las traduce utilizando un adaptador configurado.

## Cuándo usarlo

- **Nuevos Idiomas**: Cuando deseas añadir soporte para un nuevo idioma (ej. Francés) y quieres generar rápidamente un archivo `fr.json` inicial.
- **Actualización de Traducciones**: Si has añadido nuevas claves al archivo base (`es.json`) y quieres propagarlas a los demás idiomas (`en.json`, `pt.json`).
- **Prototipado Rápido**: Para obtener traducciones preliminares durante el desarrollo.

## Requisitos

Para utilizar `AutoTranslate`, necesitas:

1.  Tener instalado ToolsTranslator con el extra `[server]`.
2.  Tener acceso a un servidor de traducción (local o remoto).
3.  Configurar un adaptador de traducción (`TranslationAdapter`).

## Uso Programático

```python
from translator.core.autotranslate import AutoTranslate, AutoTranslateOptions
from translator.utils.fileinfo import TranslateFile

# Configuración
options = AutoTranslateOptions(
    langs=["en", "fr"],  # Idiomas destino
    overwrite=False      # No sobrescribir archivos existentes si ya tienen contenido
)
file_info = TranslateFile("locales/es.json")  # Archivo base

# Ejecución (requiere servidor LibreTranslate activo si use_server=True)
auto = AutoTranslate(file_info, options, use_server=True)
result = auto.worker()

print(f"Archivos generados: {result.generated_files}")
print(f"Claves traducidas: {result.translated_keys}")
```

## Dependencia del Servidor

`AutoTranslate` depende de un servicio de traducción para funcionar. Por defecto, utiliza el adaptador `LibreTranslateAdapter` que se conecta al servidor local gestionado por el CLI de ToolsTranslator.

Si no tienes un servidor local, puedes configurar un adaptador personalizado para usar otro servicio (ej. Google Translate API).

## Manejo de Errores

Si el servicio de traducción no está disponible o falla durante el proceso, `AutoTranslate` capturará la excepción `ServerDependencyMissingError` y reportará las claves fallidas en el resultado (`failed_keys`).

```python
if result.failed_keys > 0:
    print(f"Advertencia: {result.failed_keys} claves no pudieron ser traducidas.")
```
