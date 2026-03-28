# Instalación Detallada

## Requisitos Previos

- **Python** 3.10 o superior
- **Docker** (solo si usas LibreTranslate local)

## Instalación

### Opción 1: pip (recomendado)

```bash
# Básico — solo gestión de archivos de traducción
pip install toolstranslator

# Con soporte YAML
pip install toolstranslator[yml]

# Con soporte de servidor (CLI + Docker management)
pip install toolstranslator[server]

# Todo junto
pip install toolstranslator[yml,server]

# Desarrollo (tests, linting)
pip install toolstranslator[dev]
```

### Opción 2: Desde fuente

```bash
git clone https://github.com/WalterCun/ToolsTranslator.git
cd ToolsTranslator
pip install -e .
```

### Opción 3: En requirements.txt

```txt
toolstranslator>=0.2.0
toolstranslator[yml]>=0.2.0    # con YAML
toolstranslator[server]>=0.2.0  # con CLI
```

## Dependencias por Extra

| Extra | Dependencias | Para qué |
|-------|-------------|----------|
| (base) | Ninguna | Gestión de archivos JSON |
| `yml` | PyYAML >= 6.0.2 | Soporte YAML |
| `server` | typer >= 0.12.3 | CLI y gestión Docker |
| `dev` | pytest, pytest-cov, ruff | Testing y linting |

## Instalación de LibreTranslate

### Automática (recomendada)

```bash
toolstranslator install
```

Esto verifica Docker, descarga la imagen y arranca el contenedor automáticamente.

### Manual

```bash
# 1. Instalar Docker
# https://docs.docker.com/get-docker/

# 2. Descargar imagen
docker pull libretranslate/libretranslate:latest

# 3. Arrancar contenedor
docker run -d \
  --name translator-libretranslate \
  -p 5000:5000 \
  libretranslate/libretranslate:latest

# 4. Verificar
curl http://localhost:5000/languages
```

### Remoto

Si tienes un servidor LibreTranslate corriendo en otra máquina:

```python
trans = Translator(
    lang="es",
    base_url="http://mi-servidor:5000"
)
```

O por variable de entorno:
```bash
export TOOLSTRANSLATOR_BASE_URL="http://mi-servidor:5000"
```

## Problemas Comunes

### Docker no encontrado

```
✖ Docker no está instalado o no está en PATH.
```

**Solución:** Instala Docker Desktop o Docker Engine. Verifica con:
```bash
docker --version
```

### Docker daemon no activo

```
✖ Docker daemon no está activo.
```

**Solución:** Inicia Docker:
```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Abre Docker Desktop
```

### Puerto 5000 ocupado

```
✖ No se pudo iniciar/crear el contenedor
```

**Solución:** Verifica qué usa el puerto:
```bash
lsof -i :5000
# O usa otro puerto:
docker run -d --name translator-libretranslate -p 5001:5000 libretranslate/libretranslate:latest
```
Y configura: `export TOOLSTRANSLATOR_BASE_URL="http://localhost:5001"`

### Error de permisos Docker

```
permission denied while trying to connect to the Docker daemon
```

**Solución:** Agrega tu usuario al grupo docker:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Servicio no accesible después de instalar

```bash
# Ver logs del contenedor
docker logs translator-libretranslate

# Verificar que el puerto está mapeado
docker port translator-libretranslate

# Reiniciar
toolstranslator restart
```

## Verificar instalación

```bash
# CLI
toolstranslator doctor

# Python
python3 -c "from translator import Translator; print('OK')"
```
