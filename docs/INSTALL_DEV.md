# Guía de Instalación para el Entorno de Desarrollo

Esta guía detalla los pasos necesarios para configurar el entorno de desarrollo del proyecto.

## Requisitos previos

Antes de comenzar, asegúrate de cumplir con los siguientes requisitos:

- Tener Python 3.10 instalado en tu sistema.
- Tener `pip` instalado (generalmente viene con Python).
- (Opcional pero recomendado) Tener la herramienta `uv` instalada para la gestión eficiente de entornos virtuales.

## Proceso de instalación

Sigue los pasos a continuación para configurar el entorno de desarrollo:

### 1. Instalar la herramienta `uv` (opcional)

La herramienta `uv` ayuda a gestionar entornos virtuales de forma sencilla. Para instalar `uv`, ejecuta el siguiente
comando:

```bash
pip install uv
```

### 2. Inicializar `uv`

Una vez instalado, inicializa la herramienta ejecutando:

```bash
uv init
```

### 3. Crear un entorno virtual

Crea un entorno virtual utilizando Python 3.10 con el siguiente comando:

```bash
uv venv --python 3.10 .venv
```

Esto creará un entorno virtual en un directorio llamado `.venv`.

### 4. Activar el entorno virtual

Activa el entorno virtual para trabajar en un entorno aislado:

**En Windows:**

```bash
.venv\Scripts\activate
```

**En macOS/Linux:**

```bash
source .venv/bin/activate
```

### 5. Instalar las dependencias del proyecto

Una vez activado el entorno virtual, instala las dependencias del proyecto ejecutando:

```bash
uv pip install .
```

Con esto, todas las dependencias requeridas estarán instaladas en tu entorno virtual.

### 6. Instalar dependencias externas (si es necesario)

Si tu proyecto requiere el paquete `translation-tools`, puedes instalarlo usando:

**Con pipenv:**
```bash
pipenv run pip install git+https://github.com/WalterCun/ToolsTranslator.git
```

**Con uv:**
```bash
uv pip install git+https://github.com/WalterCun/ToolsTranslator.git
```

**Con pip:**
```bash
pip install git+https://github.com/WalterCun/ToolsTranslator.git
```

## Verificar la instalación

Para verificar que todo está configurado correctamente:

1. Ejecuta el proyecto e identifica si no hay errores.
2. Asegúrate de que las dependencias estén instaladas correctamente revisando el archivo `requirements.txt` (si aplica)
   o verificando manualmente las dependencias.

### Verificar translation-tools (si está instalado)

```bash
# Con pipenv
pipenv run python -c "from translator import Translator; print('✅ Translation-tools instalado correctamente')"

# Con uv o pip
python -c "from translator import Translator; print('✅ Translation-tools instalado correctamente')"
```

---

¡Listo! Ahora tu entorno de desarrollo está configurado y puedes comenzar a trabajar en el proyecto.
```