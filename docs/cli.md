# CLI de translator

translator incluye una interfaz de línea de comandos (CLI) para gestionar el servidor de traducción local basado en Docker.

## Comandos Disponibles

### `install`

Prepara y valida el entorno de ejecución de LibreTranslate paso a paso.

```bash
translator install
```

Este comando verifica:
1.  Si Docker está instalado.
2.  Si el servicio Docker está activo.
3.  Si la imagen de LibreTranslate existe (la descarga si no).
4.  Inicia el contenedor.
5.  Verifica la conectividad del servidor.

### `doctor`

Ejecuta un diagnóstico completo del entorno, similar a `flutter doctor`.

```bash
translator doctor
```

Muestra el estado de cada componente (Docker, imagen, contenedor, API) y sugiere acciones correctivas si algo falla.

### `status`

Muestra un resumen rápido del estado del servidor.

```bash
translator status
```

Salida esperada:
```
container_running=True
api_healthy=True
details=ok
```

### `restart`

Reinicia el contenedor de LibreTranslate de forma controlada.

```bash
translator restart
```

Útil si el servidor deja de responder o necesitas aplicar cambios de configuración.

### `clean-server`

Elimina el contenedor de LibreTranslate (mantiene la imagen descargada).

```bash
translator clean-server
```

Utiliza este comando si quieres empezar desde cero o liberar recursos temporalmente.

## Requisitos

Para utilizar estos comandos, asegúrate de haber instalado translator con el extra `[server]`:

```bash
pip install translator[server]
```

Y tener Docker Desktop o Docker Engine instalado y ejecutándose en tu sistema.
