# Documentación CLI

## Visión General

La CLI de ToolsTranslator se instala como `toolstranslator` y gestiona el ciclo de vida del servidor LibreTranslate.

```bash
toolstranslator [COMANDO]
```

## Comandos

### `doctor`

Diagnóstico completo del entorno. Estilo `flutter doctor`.

```bash
toolstranslator doctor
```

**Verifica:**
1. Docker instalado
2. Docker daemon activo
3. Imagen LibreTranslate disponible
4. Contenedor existe
5. Contenedor en ejecución
6. API accesible

**Códigos de salida:**
| Código | Significado |
|--------|-------------|
| 0 | Todo OK |
| 1 | Parcialmente operativo |
| 2 | No operativo |

**Ejemplo:**
```
$ toolstranslator doctor

ToolsTranslator Doctor
Analizando entorno del servidor de traducción...

✔ Docker instalado: Docker CLI detectado.
✔ Servicio Docker activo: Docker daemon responde correctamente.
✔ Imagen LibreTranslate: Imagen disponible.
✔ Contenedor LibreTranslate: Contenedor existe.
✔ Contenedor en ejecución: Contenedor en ejecución.
✔ Conectividad API LibreTranslate: Service reachable (24 languages).

✔ Listo para usar
```

### `install`

Instalación automática paso a paso.

```bash
toolstranslator install
```

**Pasos:**
1. Verifica Docker instalado
2. Verifica Docker daemon activo
3. Descarga imagen (si no existe)
4. Crea/arranca contenedor
5. Verifica conectividad API

**Ejemplo:**
```
$ toolstranslator install

ToolsTranslator Install
[1/5] Verificando Docker instalado...
✔ Docker instalado.
[2/5] Verificando servicio Docker...
✔ Docker daemon activo.
[3/5] Verificando imagen de LibreTranslate...
  Imagen no encontrada, descargando...
✔ Imagen descargada correctamente.
[4/5] Iniciando contenedor LibreTranslate...
✔ Contenedor operativo: <container_id>
[5/5] Verificando conectividad del servidor...
✔ Service reachable (24 languages).

✔ Instalación completada: entorno listo para usar.
```

### `status`

Estado rápido del servicio.

```bash
toolstranslator status
```

**Salida:**
```
container_running=True
api_healthy=True
details=Service reachable (24 languages).
```

**Útil para:** Scripts, health checks, monitoreo.

### `restart`

Reinicia el contenedor de LibreTranslate.

```bash
toolstranslator restart
```

### `clean-server`

Elimina el contenedor (preserva la imagen).

```bash
toolstranslator clean-server
```

**Útil para:** Empezar de limpio sin descargar la imagen de nuevo.

## Casos de Uso Reales

### Primera vez en un proyecto

```bash
# 1. Instalar dependencias
pip install toolstranslator[server,yml]

# 2. Verificar Docker
toolstranslator doctor

# 3. Instalar LibreTranslate
toolstranslator install

# 4. Verificar
toolstranslator status
```

### CI/CD Pipeline

```yaml
# GitHub Actions ejemplo
- name: Setup LibreTranslate
  run: |
    pip install toolstranslator[server]
    toolstranslator install
    toolstranslator status
```

### Debug de problemas

```bash
# Diagnóstico completo
toolstranslator doctor

# Ver logs del contenedor
docker logs translator-libretranslate

# Reiniciar si hay problemas
toolstranslator restart

# Eliminar y recrear
toolstranslator clean-server
toolstranslator install
```

## Configuración del Servidor

### Puerto personalizado

```bash
# Arrancar en puerto 5001
docker run -d --name translator-libretranslate -p 5001:5000 libretranslate/libretranslate:latest

# Configurar la librería
export TOOLSTRANSLATOR_BASE_URL="http://localhost:5001"
```

### Servidor remoto

```bash
export TOOLSTRANSLATOR_BASE_URL="http://mi-servidor:5000"
toolstranslator status  # Verificará contra el servidor remoto
```
