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
