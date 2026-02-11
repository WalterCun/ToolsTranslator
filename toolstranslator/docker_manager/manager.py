from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


@dataclass(slots=True)
class CheckResult:
    name: str
    ok: bool
    details: str
    suggestion: str | None = None


class DockerManager:
    """Docker utility for LibreTranslate lifecycle and diagnostics."""

    container_name = "toolstranslator-libretranslate"
    image = "libretranslate/libretranslate:latest"
    port = 5000

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(["docker", *args], text=True, capture_output=True)
        except FileNotFoundError:
            return subprocess.CompletedProcess(args=["docker", *args], returncode=127, stdout="", stderr="docker not found")

    def docker_installed(self) -> bool:
        return self._run("--version").returncode == 0

    def docker_available(self) -> bool:
        return self._run("info").returncode == 0

    def image_exists(self) -> bool:
        cmd = self._run("images", "--format", "{{.Repository}}:{{.Tag}}")
        return self.image in cmd.stdout.splitlines()

    def pull_image(self) -> tuple[bool, str]:
        cmd = self._run("pull", self.image)
        return cmd.returncode == 0, cmd.stdout.strip() or cmd.stderr.strip()

    def container_exists(self) -> bool:
        cmd = self._run("ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.Names}}")
        return self.container_name in cmd.stdout.splitlines()

    def container_running(self) -> bool:
        cmd = self._run("ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}")
        return self.container_name in cmd.stdout.splitlines()

    def start_container(self) -> tuple[bool, str]:
        if self.container_running():
            return True, "LibreTranslate container already running."
        if self.container_exists():
            start = self._run("start", self.container_name)
            return start.returncode == 0, start.stdout.strip() or start.stderr.strip()

        run = self._run(
            "run",
            "-d",
            "--name",
            self.container_name,
            "-p",
            f"{self.port}:5000",
            self.image,
        )
        return run.returncode == 0, run.stdout.strip() or run.stderr.strip()

    def restart_container(self) -> tuple[bool, str]:
        if not self.container_exists():
            return False, "Container does not exist."
        cmd = self._run("restart", self.container_name)
        return cmd.returncode == 0, cmd.stdout.strip() or cmd.stderr.strip()

    def remove_container(self) -> tuple[bool, str]:
        if not self.container_exists():
            return True, "Container does not exist."
        cmd = self._run("rm", "-f", self.container_name)
        return cmd.returncode == 0, cmd.stdout.strip() or cmd.stderr.strip()

    def healthcheck(self, timeout_s: float = 2.0) -> tuple[bool, str]:
        url = f"http://localhost:{self.port}/languages"
        try:
            with urlopen(url, timeout=timeout_s) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body)
                if isinstance(data, list):
                    return True, f"Service reachable ({len(data)} languages)."
                return True, "Service reachable."
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            return False, f"Service not reachable at {url}: {exc}"

    def diagnostics(self) -> list[CheckResult]:
        checks: list[CheckResult] = []

        docker_installed = self.docker_installed()
        checks.append(
            CheckResult(
                name="Docker instalado",
                ok=docker_installed,
                details="Docker CLI detectado." if docker_installed else "No se encontró el ejecutable docker.",
                suggestion="Instala Docker Desktop/Engine y asegúrate de que `docker --version` funcione.",
            )
        )
        if not docker_installed:
            return checks

        docker_running = self.docker_available()
        checks.append(
            CheckResult(
                name="Servicio Docker activo",
                ok=docker_running,
                details="Docker daemon responde correctamente." if docker_running else "Docker daemon no responde.",
                suggestion="Inicia Docker service/Desktop y vuelve a ejecutar `toolstranslator doctor`.",
            )
        )
        if not docker_running:
            return checks

        image_ok = self.image_exists()
        checks.append(
            CheckResult(
                name="Imagen LibreTranslate",
                ok=image_ok,
                details=f"Imagen `{self.image}` disponible." if image_ok else f"Imagen `{self.image}` no encontrada.",
                suggestion=f"Ejecuta `docker pull {self.image}` o `toolstranslator install`.",
            )
        )

        exists = self.container_exists()
        running = self.container_running() if exists else False
        checks.append(
            CheckResult(
                name="Contenedor LibreTranslate",
                ok=exists,
                details=f"Contenedor `{self.container_name}` existe." if exists else "Contenedor no existe.",
                suggestion=f"Ejecuta `toolstranslator install` para crearlo.",
            )
        )
        checks.append(
            CheckResult(
                name="Contenedor en ejecución",
                ok=running,
                details="Contenedor en ejecución." if running else "Contenedor detenido.",
                suggestion=f"Ejecuta `docker start {self.container_name}` o `toolstranslator install`.",
            )
        )

        healthy, details = self.healthcheck()
        checks.append(
            CheckResult(
                name="Conectividad API LibreTranslate",
                ok=healthy,
                details=details,
                suggestion=f"Verifica puertos y logs del contenedor: `docker logs {self.container_name}`.",
            )
        )
        return checks
