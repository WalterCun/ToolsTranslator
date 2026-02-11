# Arquitectura

## Objetivo
Mantener compatibilidad funcional del proyecto original y desacoplar componentes para escalar en PyPI.

## Problemas detectados en la arquitectura previa

- Acoplamiento fuerte entre CLI, lógica de archivos y cliente HTTP.
- Riesgo de perder comportamientos históricos (`lang` mutable, proxy por atributos, auto-add de claves).
- Manejo de archivos sin garantías de escritura atómica.
- Ausencia de estrategia clara de cache y recarga por idioma.

## Módulos

- `toolstranslator/core`: API pública (`Translator`) y `TranslationProxy`.
- `toolstranslator/adapters`: cliente HTTP y adapter LibreTranslate.
- `toolstranslator/file_handlers`: JSON base + YAML opcional lazy.
- `toolstranslator/docker_manager`: integración Docker para CLI server.
- `toolstranslator/cli`: interfaz Typer (extra `server`).

## Contrato de compatibilidad (obligatorio)

1. `lang` como propiedad pública mutable y persistente.
2. `auto_add_missing_keys` configurable en constructor y en caliente.
3. Proxy dinámico con `__getattr__` y soporte de claves anidadas.
4. Fallback seguro cuando falta clave/idioma.
5. No romper ejecución por claves faltantes.

## Seguridad de resolución dinámica (`__getattr__`)

- Solo se activa para atributos no existentes.
- Ignora atributos internos (`_...`) para evitar colisiones.
- Usa `TranslationProxy` para encadenar `trans.a.b.c`.

## Escritura concurrente y prevención de corrupción

- Escritura atómica en handlers (tmp + `os.replace`).
- Bloqueo de instancia (`RLock`) durante alta automática de claves faltantes.

## Flujo principal

- `Translator.get` / `Translator.__getattr__` -> resolución local por idioma activo.
- Si valor dinámico (`__translate__`) -> `LibreTranslateClient`.
- Cache por `(lang, key)` para claves resueltas.
