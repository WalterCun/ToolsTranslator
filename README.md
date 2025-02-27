# ToolsTranslator

ToolsTranslator es una librería para realizar traducciones de texto de forma eficiente.

## Instalación
```bash
pip install ToolsTranslator
```

## Uso
```python
from ToolsTranslator.core import translate

# Traducción de un texto
result = translate("Hola", target_language="en")
print(result)  # Output: "Hello"
```

# Configuración del proyecto

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

## Requisitos previos

- Python 3.10 instalado.
- Herramienta `uv` instalada (opcional, pero recomendada para mayor velocidad).

## Instalación

``` cmd | powershell
pip install uv
```

``` cmd | powershell
uv init
```

``` cmd | powershell
uv venv --python 3.10 .venv
```

``` cmd | powershell
.venv\Scripts\activate 
```

``` cmd | powershell
uv pip install .
```
