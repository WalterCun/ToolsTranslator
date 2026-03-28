# ToolsTranslator

Librería Python para gestión de traducciones i18n con soporte opcional para traducción automática mediante LibreTranslate.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ¿Qué es?

**ToolsTranslator** te permite gestionar archivos de traducción (`.json`, `.yaml`) en tus proyectos Python de forma simple, con acceso dinámico a las claves mediante atributos y soporte opcional para traducción automática vía LibreTranslate.

## Características

- 📁 **Gestión de archivos de idioma** — Carga y escritura de `.json` y `.yaml`/`.yml`
- 🎯 **Acceso dinámico** — `trans.home.title` en vez de diccionarios anidados
- 🌐 **Traducción automática** — Genera archivos de idioma con LibreTranslate
- 🔄 **Cambio de idioma en runtime** — `trans.change_lang("es")`
- 🛡️ **Claves faltantes** — Auto-detección y registro automático
- 🔌 **Adapter personalizable** — Inyecta tu propio backend de traducción
- ⚡ **Cache inteligente** — TTL cache para verificaciones de servidor
- 🧵 **Thread-safe** — Seguro para uso concurrente

## Instalación

### Básica (solo gestión de archivos)

```bash
pip install toolstranslator
```

### Con soporte YAML

```bash
pip install toolstranslator[yml]
```

### Con soporte para servidor (CLI + Docker)

```bash
pip install toolstranslator[server]
```

### Requisitos

- Python 3.10+
- Docker (solo si usas LibreTranslate local)

## Inicio Rápido

### Como librería

```python
from translator import Translator

# Asume que tienes locales/en.json con:
# {"greeting": {"title": "Welcome", "button": "Enter"}}

trans = Translator(lang="es", directory="./locales")

# Acceso por atributos
print(trans.greeting.title)       # "Bienvenido"
print(trans.get("greeting.button"))  # "Entrar"

# Cambiar idioma
trans.change_lang("en")
print(trans.greeting.title)       # "Welcome"
```

### Como CLI

```bash
# Verificar entorno
toolstranslator doctor

# Instalar LibreTranslate
toolstranslator install

# Ver estado
toolstranslator status
```

## Uso como CLI

### Comandos disponibles

| Comando | Descripción |
|---------|-------------|
| `toolstranslator doctor` | Diagnóstico completo del entorno (estilo `flutter doctor`) |
| `toolstranslator install` | Instalación automática de LibreTranslate (Docker) |
| `toolstranslator status` | Estado rápido del servicio |
| `toolstranslator restart` | Reiniciar contenedor de LibreTranslate |
| `toolstranslator clean-server` | Eliminar contenedor (preserva imagen) |

### Ejemplo de salida de `doctor`

```
$ toolstranslator doctor

ToolsTranslator Doctor
Analizando entorno del servidor de traducción...

✔ Docker instalado: Docker CLI detectado.
✔ Servicio Docker activo: Docker daemon responde correctamente.
✔ Imagen LibreTranslate: Imagen disponible.
✔ Contenedor LibreTranslate: Contenedor existe.
✔ Contenedor en ejecución: Contenedor en ejecución.
✔ Conectividad API LibreTranslate: Service reachable (24 languages).

✔ Listo para usar
```

## Uso como librería

### Acceso a traducciones

```python
from translator import Translator

trans = Translator(lang="es", directory="./locales")

# Opción 1: Acceso por atributos (recomendado)
title = trans.home.title

# Opción 2: Acceso por clave con puntos
title = trans.get("home.title")

# Opción 3: Con valor por defecto
title = trans.get("missing.key", default="Valor por defecto")
```

### Cambio de idioma

```python
trans.change_lang("en")  # Método
trans.lang = "fr"         # Property
```

### Claves faltantes

```python
# Auto-agregar claves faltantes al archivo
trans = Translator(lang="es", directory="./locales", auto_add_missing_keys=True)
trans.get("new.key")  # Agrega al archivo con valor "TODO: agregar traducción"

# Comportamiento personalizado
trans = Translator(lang="es", directory="./locales", missing_key_behavior="message")
trans.get("missing")  # Retorna "Missing translation"

# Con fallback
trans = Translator(lang="es", directory="./locales", fallback_lang="en")
```

### Traducción directa (requiere LibreTranslate)

```python
trans = Translator(lang="es", base_url="http://localhost:5000")

# Traducir texto
translated = trans.translate("Hello world", source="en", target="es")

# Con fallback si falla
translated = trans.translate("Hello", fallback="Error de traducción")

# Async
translated = await trans.translate_async("Hello", source="en", target="es")
```

### Adapter personalizado

```python
from translator import Translator, TranslationAdapter

class MiAdapter:
    def available(self) -> tuple[bool, str]:
        return True, "ok"

    def translate(self, text: str, source: str, target: str) -> str:
        return f"[{target}] {text}"

trans = Translator(lang="es", adapter=MiAdapter())
```

## Configuración

### Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `TOOLSTRANSLATOR_BASE_URL` | `http://localhost:5000` | URL del servidor LibreTranslate |
| `TOOLSTRANSLATOR_TIMEOUT` | `10` | Timeout HTTP en segundos |
| `TOOLSTRANSLATOR_SOURCE_LANG` | `auto` | Idioma fuente por defecto |
| `TOOLSTRANSLATOR_TARGET_LANG` | `en` | Idioma destino por defecto |
| `TOOLSTRANSLATOR_LOCALE_DIR` | `./locales` | Directorio de archivos de idioma |
| `TOOLSTRANSLATOR_MISSING_KEY` | `key` | Comportamiento: `key` o `message` |
| `TOOLSTRANSLATOR_LOG_LEVEL` | `INFO` | Nivel de logging |

## Manejo de errores

```python
from translator.exceptions import (
    ServiceUnavailableError,
    LanguageNotAvailableError,
    TranslationFileError,
)

try:
    result = trans.translate("Hola", target="en")
except ServiceUnavailableError:
    print("LibreTranslate no está corriendo")

try:
    trans.change_lang("xx")
except LanguageNotAvailableError as e:
    print(f"Idioma no disponible: {e}")
```

## Contribución

1. Fork el repositorio
2. Crea una rama: `git checkout -b fix/mi-mejora`
3. Instala dependencias: `pip install toolstranslator[dev]`
4. Ejecuta tests: `pytest tests/ -v`
5. Abre un Pull Request

## Licencia

MIT — ver [LICENSE](LICENSE).
