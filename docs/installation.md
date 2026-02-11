# Instalación

ToolsTranslator ofrece diferentes opciones de instalación según tus necesidades.

## Requisitos Previos

- Python 3.10 o superior.
- (Opcional) Docker Desktop o Docker Engine para usar el servidor de traducción local.

## Instalación Básica

Para utilizar ToolsTranslator como gestor de archivos de idioma (JSON) y proxy de traducción:

```bash
pip install toolstranslator
```

## Instalación con Soporte YAML

Si necesitas trabajar con archivos `.yaml` o `.yml`:

```bash
pip install toolstranslator[yml]
```

## Instalación Completa (Servidor)

Para habilitar todas las funcionalidades, incluyendo el CLI para gestionar el servidor de traducción local y la generación automática de archivos:

```bash
pip install toolstranslator[server]
```

Esta opción instala dependencias adicionales como `typer` y `httpx`.

## Verificación de la Instalación

Puedes verificar que la instalación fue exitosa ejecutando:

```bash
python -c "import translator; print(translator.__file__)"
```

Si instalaste con `[server]`, también puedes probar el comando CLI:

```bash
translator --help
```
