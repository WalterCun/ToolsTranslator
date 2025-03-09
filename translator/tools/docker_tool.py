# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/tools/docker_tools.py """

import subprocess


def is_docker_running():
    try:
        result = subprocess.run(["docker", "info"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_docker_installed():
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False


if __name__ == "__main__":
    if is_docker_installed():
        print("Docker está instalado." if is_docker_installed() else "Docker no está instalado.")
        print("Docker está en ejecución." if is_docker_running() else "Docker no está corriendo o no está instalado.")

    else:
        print("Docker no está instalado.")
