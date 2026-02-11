from __future__ import annotations

import subprocess


class DockerManager:
    """Docker utility for LibreTranslate lifecycle."""

    container_name = "translator-libretranslate"
    image = "libretranslate/libretranslate:latest"

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["docker", *args], text=True, capture_output=True)

    def docker_available(self) -> bool:
        return self._run("info").returncode == 0

    def container_exists(self) -> bool:
        cmd = self._run("ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.Names}}")
        return self.container_name in cmd.stdout.splitlines()

    def container_running(self) -> bool:
        cmd = self._run("ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}")
        return self.container_name in cmd.stdout.splitlines()

    def ensure_running(self) -> tuple[bool, str]:
        if not self.docker_available():
            return False, "Docker is not available."
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
            "5000:5000",
            self.image,
        )
        return run.returncode == 0, run.stdout.strip() or run.stderr.strip()
