# Arquitectura

## Objetivo
Diseño modular desacoplado con comportamiento controlado por extras.

## Problemas detectados en la arquitectura previa

- Acoplamiento fuerte entre CLI, lógica de archivos y cliente HTTP.
- Carga temprana de funcionalidades opcionales (YAML/auto) sin aislar extras.
- API pública mezclada con lógica de inicialización y validaciones de entorno.
- Integración Docker dispersa y difícil de reutilizar desde comandos CLI.
- Falta de separación explícita entre SDK (reutilizable) y herramientas operativas.

## Módulos

- `toolstranslator/core`: API pública (`Translator`).
- `toolstranslator/adapters`: cliente HTTP y adapter LibreTranslate.
- `toolstranslator/file_handlers`: JSON base + YAML opcional lazy.
- `toolstranslator/docker_manager`: integración Docker para CLI server.
- `toolstranslator/cli`: interfaz Typer (extra `server`).

## Principios

1. **Dependencias mínimas en instalación base**.
2. **Lazy loading para YAML** usando import dinámico.
3. **CLI aislada en extra server**.
4. **SDK reutilizable** independiente del CLI.
5. **Manejo robusto de errores** mediante excepciones específicas.

## Flujo principal

`Translator.translate` -> `LibreTranslateClient` -> `HttpClient` -> LibreTranslate.

## Configuración

Variables de entorno prefijadas con `TOOLSTRANSLATOR_`.
