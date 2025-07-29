# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/tools/verify_docker_tools.py """

import platform
import subprocess
import sys
import os
import logging
from time import sleep

from docker_tool import manage_libretranslate
from translator.tools.docker_tool import is_docker_installed, is_docker_running

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def ask_confirmation(question):
    """Pregunta al usuario si desea continuar."""
    answer = input(f"{question} (y/n): ").strip().lower()
    return answer == "y"


def install_docker():
    """Instala Docker según el sistema operativo."""
    system = platform.system()

    if not ask_confirmation("Docker no está instalado. ¿Deseas instalarlo ahora?"):
        logging.info("Instalación cancelada por el usuario.")
        sys.exit(0)

    if system == "Windows":
        logging.info("Instalando Docker Desktop en Windows...")
        url = "https://desktop.docker.com/win/main/amd64/Docker Desktop Installer.exe"
        installer_path = os.path.join(os.getenv("TEMP", "C:\\Windows\\Temp"), "DockerInstaller.exe")
        subprocess.run(["curl", "-L", url, "-o", installer_path], check=True)
        subprocess.run([installer_path, "/quiet"], check=True)
        logging.info("Docker instalado. Reinicia el sistema para completar la instalación.")

    elif system == "Darwin":  # macOS
        logging.info("Instalando Docker Desktop en macOS...")
        url = "https://desktop.docker.com/mac/main/amd64/Docker.dmg"
        subprocess.run(["curl", "-L", url, "-o", "/tmp/Docker.dmg"], check=True)
        subprocess.run(["hdiutil", "attach", "/tmp/Docker.dmg"], check=True)
        subprocess.run(["cp", "-R", "/Volumes/Docker/Docker.app", "/Applications"], check=True)
        subprocess.run(["hdiutil", "detach", "/Volumes/Docker"], check=True)
        logging.info("Docker instalado. Inicia Docker desde Aplicaciones.")

    elif system == "Linux":
        logging.info("Instalando Docker en Linux...")
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "docker.io"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "--now", "docker"], check=True)
        logging.info("Docker instalado y en ejecución.")

    else:
        logging.error("Sistema operativo no soportado para instalación automática.")
        sys.exit(1)


def start_docker():
    """Inicia Docker si está instalado pero no ejecutándose."""
    system = platform.system()

    if not ask_confirmation("Docker está instalado pero no en ejecución. ¿Deseas iniciarlo ahora?"):
        logging.info("El usuario decidió no iniciar Docker.")
        sys.exit(0)

    if system == "Windows":
        logging.info("Intentando iniciar Docker en Windows...")
        subprocess.run(
            ["powershell", "-Command", "Start-Process 'C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe'"],
            check=True)

    elif system == "Darwin":  # macOS
        logging.info("Intentando iniciar Docker en macOS...")
        subprocess.run(["open", "--background", "-a", "Docker"], check=True)

    elif system == "Linux":
        logging.info("Intentando iniciar Docker en Linux...")
        subprocess.run(["sudo", "systemctl", "start", "docker"], check=True)

    else:
        logging.error("No se puede iniciar Docker automáticamente en este sistema.")
        sys.exit(1)


def validator_docker_container():
    """Verifica Docker e intenta instalarlo o iniciarlo si es necesario."""
    if not is_docker_installed():
        logging.warning("Docker no está instalado.")
        install_docker()
    elif not is_docker_running():
        logging.warning("Docker está instalado pero no en ejecución.")
        start_docker()
        sleep(20)
    else:
        logging.info("Docker está instalado y en ejecución.")
    manage_libretranslate()

# if __name__ == "__main__":
#     ensure_docker()
