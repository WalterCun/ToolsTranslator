# Guía: LibreTranslate con Docker

El paquete translation-tools utiliza LibreTranslate como servicio HTTP (por defecto en http://localhost:5000) para detección y traducción de idiomas. A continuación se explica cómo iniciarlo usando las utilidades incluidas.

Advertencias importantes

- Las utilidades pueden intentar instalar o iniciar Docker en tu equipo (con confirmación), lo cual está orientado a entornos de desarrollo. En servidores CI, o si no deseas este comportamiento, ejecuta tu propio LibreTranslate y desactiva las utilidades.
- La instalación/descarga de imágenes puede demorar varios minutos la primera vez.

Opciones recomendadas

1) Usar el helper de validación (interactivo)

```python
from bk.tools.verify_docker_tool import validator_docker_container

# Verifica si Docker está instalado y corriendo; si no, preguntará para instalar/iniciar.
# Luego intentará asegurar un contenedor de LibreTranslate en ejecución.
validator_docker_container()
```

2) Gestionar directamente LibreTranslate con Docker (programático)

```python
from bk.tools.docker_tool import manage_libretranslate, get_libretranslate_status, is_docker_installed, is_docker_running

print("Docker instalado:", is_docker_installed())
print("Docker en ejecución:", is_docker_running())

# Intenta usar una imagen disponible; si no existe, probará descargarla o construirla.
result = manage_libretranslate()
print(result)

print("Estado de LibreTranslate:", get_libretranslate_status())
```

3) Iniciar manualmente con Docker (línea de comandos)

Si prefieres, puedes correr LibreTranslate sin las utilidades del paquete:

```powershell
# Imagen oficial (puede variar según la versión)
docker run -d --name libretranslate -p 5000:5000 libretranslate/libretranslate:latest
```

Luego verifica que http://localhost:5000 responda.

Solución de problemas

- El puerto 5000 está ocupado: Ajusta el mapeo de puertos, por ejemplo `-p 5001:5000` y configura tu aplicación para usar `http://localhost:5001`.
- Permisos de Docker en Linux: asegúrate de pertenecer al grupo `docker` o usa `sudo` para ejecutar comandos.
- Redes corporativas/Proxy: la descarga de imágenes puede requerir configuración adicional del proxy de Docker.
