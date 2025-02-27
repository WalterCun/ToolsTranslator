import os
import subprocess
import logging
import time
import requests

from tools.verify_docker_tool import ensure_docker

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

LIBRETRANSLATE_REPO = "https://github.com/LibreTranslate/LibreTranslate"
SERVICE_URL = "http://localhost:5000"
REPO_DIR = "LibreTranslate"

def is_service_running():
    """Verifica si LibreTranslate está corriendo en localhost:5000."""
    try:
        response = requests.get(SERVICE_URL, timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False

def clone_repo():
    """Clona el repositorio de LibreTranslate si no existe."""
    if not os.path.exists(REPO_DIR):
        logging.info(f"Clonando LibreTranslate desde {LIBRETRANSLATE_REPO}...")
        subprocess.run(["git", "clone", LIBRETRANSLATE_REPO], check=True)
    else:
        logging.info("El repositorio de LibreTranslate ya existe, verificando actualizaciones...")
        subprocess.run(["git", "-C", REPO_DIR, "pull"], check=True)

def start_libretranslate():
    """Inicia el servicio LibreTranslate con Docker Compose."""
    os.chdir(REPO_DIR)

    logging.info("Intentando iniciar LibreTranslate con CUDA...")
    result = subprocess.run(["docker", "compose", "-f", "docker-compose.cuda.yml", "up", "-d", "--build"], stderr=subprocess.PIPE)

    if result.returncode != 0:
        logging.warning("Error con CUDA, intentando con la configuración estándar...")
        subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "up", "-d", "--build"], check=True)

    os.chdir("..")  # Volver al directorio original

def ensure_libretranslate():
    """Verifica e inicia LibreTranslate si no está corriendo."""
    logging.info("Verificando si LibreTranslate está ejecutándose...")

    if is_service_running():
        logging.info("LibreTranslate ya está corriendo en localhost:5000")
        return

    logging.warning("LibreTranslate no está corriendo. Iniciando instalación...")

    # Asegurar que Docker está instalado y ejecutándose
    ensure_docker()

    # Descargar e iniciar LibreTranslate
    clone_repo()
    start_libretranslate()

    # Esperar unos segundos y verificar nuevamente
    time.sleep(10)
    if is_service_running():
        logging.info("LibreTranslate se inició correctamente.")
    else:
        logging.error("No se pudo iniciar LibreTranslate.")

if __name__ == "__main__":
    ensure_libretranslate()
    # print(REPO_DIR)