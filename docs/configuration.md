# Configuración

## Variables de Entorno

Todas las variables se leen al importar el módulo. Para cambiar valores en runtime, pasa los parámetros directamente al constructor.

| Variable | Default | Descripción |
|----------|---------|-------------|
| `TOOLSTRANSLATOR_BASE_URL` | `http://localhost:5000` | URL del servidor LibreTranslate |
| `TOOLSTRANSLATOR_TIMEOUT` | `10` | Timeout HTTP en segundos |
| `TOOLSTRANSLATOR_SOURCE_LANG` | `auto` | Idioma fuente por defecto (auto=detección) |
| `TOOLSTRANSLATOR_TARGET_LANG` | `en` | Idioma destino por defecto |
| `TOOLSTRANSLATOR_LOCALE_DIR` | `./locales` | Directorio de archivos de idioma |
| `TOOLSTRANSLATOR_MISSING_KEY` | `key` | Comportamiento ante claves faltantes |
| `TOOLSTRANSLATOR_LOG_LEVEL` | `INFO` | Nivel de logging |

## Ejemplos de Configuración

### Proyecto local con LibreTranslate

```bash
export TOOLSTRANSLATOR_BASE_URL="http://localhost:5000"
export TOOLSTRANSLATOR_LOCALE_DIR="./src/locales"
export TOOLSTRANSLATOR_LOG_LEVEL="DEBUG"
```

### Servidor remoto

```bash
export TOOLSTRANSLATOR_BASE_URL="https://translate.miempresa.com"
export TOOLSTRANSLATOR_TIMEOUT="30"
```

### Solo gestión de archivos (sin servidor)

```python
# No necesitas configurar TOOLSTRANSLATOR_BASE_URL si no usas translate()
from translator import Translator
trans = Translator(lang="es", directory="./locales")
```

## Niveles de Logging

| Nivel | Qué muestra |
|-------|-------------|
| `DEBUG` | Todo: cambios de idioma, claves faltantes, cache hits |
| `INFO` | Auto-add de claves, operaciones significativas |
| `WARNING` | Fallbacks, degradaciones |
| `ERROR` | Fallos de traducción, archivos corruptos |

```bash
export TOOLSTRANSLATOR_LOG_LEVEL="DEBUG"
```

O desde Python:

```python
import logging
logging.getLogger("translator").setLevel(logging.DEBUG)
```

## Estructura de Archivos de Idioma

### Formato JSON (recomendado)

```json
{
  "app": {
    "title": "Mi Aplicación",
    "buttons": {
      "save": "Guardar",
      "cancel": "Cancelar"
    }
  },
  "greeting": "Hola {{name}}"
}
```

### Formato YAML

```yaml
app:
  title: Mi Aplicación
  buttons:
    save: Guardar
    cancel: Cancelar
greeting: "Hola {{name}}"
```

### Valores dinámicos

```json
{
  "welcome": {
    "__translate__": "Welcome to our app",
    "source": "en",
    "target": "es"
  }
}
```

Al acceder a `trans.welcome`, se ejecuta `translate("Welcome to our app", "en", "es")`.

### Convenciones de nombres

Los archivos se buscan en orden:
1. `{lang}.json`
2. `{lang}.yaml`
3. `{lang}.yml`

Ejemplos válidos: `en.json`, `es.yaml`, `pt_BR.yml`, `zh_Hans.json`
