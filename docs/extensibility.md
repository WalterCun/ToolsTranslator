# Extensibilidad

## Nuevos adapters
Crear implementaciones en `toolstranslator/adapters` y usarlas desde `Translator`.

## Nuevos file handlers
Agregar handler en `toolstranslator/file_handlers` y extender el enrutamiento en `Translator._read_file/_write_file`.

## Nuevos comandos CLI
Agregar comandos Typer en `toolstranslator/cli/app.py`.

## Asincronía
`Translator.translate_async` permite integrar flujos async (FastAPI, workers async).
