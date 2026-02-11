# Configuración

ToolsTranslator utiliza variables de entorno para configurar su comportamiento por defecto. Esto permite adaptar la librería a diferentes entornos (desarrollo, producción) sin modificar el código.

## Variables de Entorno

Las siguientes variables pueden definirse en tu archivo `.env` o en el entorno del sistema:

| Variable | Descripción | Valor por Defecto |
| :--- | :--- | :--- |
| `TOOLSTRANSLATOR_BASE_URL` | URL base del servidor LibreTranslate. | `http://localhost:5000` |
| `TOOLSTRANSLATOR_TIMEOUT` | Tiempo de espera (en segundos) para las peticiones HTTP. | `10` |
| `TOOLSTRANSLATOR_SOURCE_LANG` | Idioma fuente por defecto para traducciones automáticas. | `auto` |
| `TOOLSTRANSLATOR_TARGET_LANG` | Idioma destino por defecto. | `en` |
| `TOOLSTRANSLATOR_LOCALE_DIR` | Directorio donde se buscan/guardan los archivos de idioma. | `./locales` |
| `TOOLSTRANSLATOR_MISSING_KEY` | Comportamiento ante claves faltantes (`key`, `message`). | `key` |
| `TOOLSTRANSLATOR_LOG_LEVEL` | Nivel de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | `INFO` |

## Configuración en Código

También puedes sobrescribir estos valores al instanciar la clase `Translator`:

```python
from translator import Translator

trans = Translator(
    base_url="http://mi-servidor-traduccion:5000",
    timeout=5.0,
    directory="/app/locales",
    missing_key_behavior="message"
)
```

## Comportamiento de Claves Faltantes (`missing_key_behavior`)

- **`key`**: Devuelve el nombre de la clave solicitada si no se encuentra traducción.
- **`message`**: Devuelve el mensaje "Missing translation".

## Auto Add Missing Keys (`auto_add_missing_keys`)

Esta opción no se configura por variable de entorno, sino directamente en el constructor de `Translator`.

- **`True`**: Crea automáticamente la clave faltante en el archivo de idioma con el valor "TODO: agregar traducción".
- **`False`**: No modifica el archivo (comportamiento por defecto).
