import pytest


typer_testing = pytest.importorskip("typer.testing")
CliRunner = typer_testing.CliRunner

from translator.cli.app import app


class _DoctorOkManager:
    def diagnostics(self):
        from translator.docker_manager.manager import CheckResult

        return [
            CheckResult("Docker instalado", True, "ok"),
            CheckResult("Servicio Docker activo", True, "ok"),
        ]


class _InstallFailManager:
    image = "libretranslate/libretranslate:latest"
    container_name = "translator-libretranslate"

    def docker_installed(self):
        return True

    def docker_available(self):
        return True

    def image_exists(self):
        return False

    def pull_image(self):
        return False, "network error"


def test_doctor_reports_ready(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr("translator.cli.app.DockerManager", _DoctorOkManager)
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "Listo para usar" in result.stdout


def test_install_reports_actionable_error(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr("translator.cli.app.DockerManager", _InstallFailManager)
    result = runner.invoke(app, ["install"])

    assert result.exit_code == 2
    assert "Error al descargar imagen" in result.stdout
    assert "docker pull" in result.stdout
