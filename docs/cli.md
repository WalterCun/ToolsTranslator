# CLI

> Requiere `pip install toolstranslator[server]`

La CLI ya no opera en silencio. Todos los comandos muestran progreso, estado y acciones sugeridas.

## `toolstranslator doctor`

Diagnóstico completo estilo *doctor* con reporte por checks:

- Docker instalado
- Servicio Docker activo
- Imagen LibreTranslate disponible
- Contenedor existente/en ejecución
- Conectividad de API (`/languages`)

Salida final:

- `✔ Listo para usar`
- `⚠ Parcialmente listo`
- `✖ No operativo`

Cada fallo incluye una sugerencia accionable (comando recomendado).

## `toolstranslator install`

Provisiona el entorno de servidor paso a paso:

1. Verifica Docker instalado.
2. Verifica daemon Docker.
3. Descarga imagen de LibreTranslate (si falta).
4. Crea/inicia contenedor.
5. Valida conectividad HTTP del servicio.

En cada paso imprime progreso y, ante error, explica causa y cómo resolver.

## Nuevos comandos recomendados y añadidos

### `toolstranslator status`
Chequeo rápido de `container_running` + `api_healthy`.

### `toolstranslator restart`
Reinicia el contenedor LibreTranslate de forma controlada.

### `toolstranslator clean-server`
Elimina contenedor para limpieza de entorno (conserva imagen).
