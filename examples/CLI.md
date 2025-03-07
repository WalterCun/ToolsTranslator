# Uso de la Librería Desde la Línea de Comandos (CLI)

Este documento explica cómo usar la librería a través de la interfaz de línea de comandos (CLI). Puedes ejecutar el comando principal `auto_translate` con varios argumentos para traducir archivos estructurados como JSON o YAML a diferentes idiomas.

---

## Instalación del CLI

Antes de usar la CLI, asegúrate de tener Python 3.10 (o superior) instalado en tu máquina y de que la librería esté instalada en tu entorno.

### Instalar la librería

Si aún no has instalado la librería, puedes hacerlo ejecutando:

```bash
pip install nombre_de_tu_libreria
```

---

## Estructura del Comando

El comando básico para usar la librería en la consola tiene la forma:

```bash
python cli.py auto_translate [ruta_al_archivo] [opciones]
```

### Descripción de Argumentos y Opciones

- **`auto_translate`**: El comando principal que activa el proceso de traducción.
- **`ruta_al_archivo`**: La ruta al archivo JSON o YAML que deseas traducir. Ejemplo: `D:\Coders\ToolsTranslator\struct_files\en.json`.

#### Opciones Disponibles:

| Opción           | Descripción                                                                                   | Obligatorio | Valores Posibles            |
|-------------------|-----------------------------------------------------------------------------------------------|-------------|-----------------------------|
| `--lang`         | Idioma objetivo para la traducción.                                                           | Sí          | `es`, `br`, `all`, etc.     |
| `--output`       | Directorio de salida donde se guardará el archivo traducido. Si no se especifica, usa el actual. | No          | Ruta del directorio         |
| `--overwrite`    | Indica si se debe sobrescribir el archivo de salida en caso de que ya exista.                  | No          | No acepta valores adicionales (bandera). |

---

## Ejemplos de Uso

A continuación se presentan diferentes casos prácticos de cómo ejecutar la librería desde la terminal:

### 1. Traducir un archivo JSON al idioma español

```bash
python cli.py auto_translate D:\Coders\ToolsTranslator\struct_files\en.json --lang es
```

**Explicación:**
- Traduce el archivo `en.json` a español (`--lang es`).
- El archivo traducido se guardará en el mismo directorio (por defecto).

---

### 2. Traducir un archivo JSON a todos los idiomas disponibles

```bash
python cli.py auto_translate D:\Coders\ToolsTranslator\struct_files\en.json --lang all
```

**Explicación:**
- Traduce el archivo `en.json` a todos los idiomas soportados (`--lang all`).
- El archivo traducido para cada idioma se guardará en el directorio predeterminado.

---

### 3. Traducir un archivo YAML al idioma portugués (brasileño)

```bash
python cli.py auto_translate D:\Coders\ToolsTranslator\struct_files\en.yml --lang br
```

**Explicación:**
- Traduce el archivo `en.yml` al idioma portugués (`--lang br`).

---

### 4. Traducir y guardar el resultado en un directorio específico

```bash
python cli.py auto_translate D:\Coders\ToolsTranslator\struct_files\en.json --lang all --output D:\Coders\ToolsTranslator\struct_files\output
```

**Explicación:**
- Traduce el archivo `en.json` a todos los idiomas soportados (`--lang all`).
- Los archivos traducidos se guardarán en el directorio `output`.

---

### 5. Sobrescribir archivos existentes durante la traducción

```bash
python cli.py auto_translate D:\Coders\ToolsTranslator\struct_files\en.json --lang es --output D:\Coders\ToolsTranslator\struct_files\output --overwrite
```

**Explicación:**
- Traduce el archivo `en.json` al español (`--lang es`).
- Guarda el resultado en `output`.
- Sobrescribe el archivo en caso de que ya exista.

---

## Resolución de Problemas

### Error: `command not found`

Si recibes este error, verifica que Python esté instalado correctamente y que la librería esté accesible desde tu terminal. Asegúrate de ejecutar el comando desde el directorio donde se encuentra el archivo `cli.py`.

### Error: **El archivo proporcionado no existe.**

Asegúrate de que la ruta que has ingresado al archivo JSON o YAML es correcta. Por ejemplo:

```bash
python cli.py auto_translate "D:\ruta_correcta\a_los_archivos\archivo.json" --lang en
```

---

## Ayuda

Puedes usar la siguiente opción para obtener ayuda sobre cómo usar el CLI:

```bash
python cli.py --help
```

Esto proporcionará una lista de los comandos y opciones disponibles.

---

## Integración con Scripts

Puedes integrar este CLI en scripts bash o workflows para traducir múltiples archivos automáticamente:

**Ejemplo:**

```bash
for archivo in ./archivos_a_traducir/*.json; do
    python cli.py auto_translate "$archivo" --lang all --output ./output --overwrite
done
```

Este script recorrerá archivos JSON en un directorio y los traducirá a todos los idiomas soportados, guardando los resultados en un directorio de salida.

---

## Conclusión

Este archivo detalla el uso del CLI para traducir archivos JSON y YAML con facilidad. Si tienes preguntas adicionales, revisa la documentación completa del proyecto o abre un [Issue](https://github.com/usuario/repositorio/issues).

¡Esperamos que encuentres útil esta herramienta! 🚀