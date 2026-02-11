from __future__ import annotations

import typer

from toolstranslator.docker_manager.manager import CheckResult, DockerManager
from toolstranslator.exceptions import ExtraNotInstalledError

app = typer.Typer(help="ToolsTranslator CLI")


def _ensure_server_extra() -> None:
    try:
        import typer as _  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise ExtraNotInstalledError(
            "Server commands require extra dependencies. Install: pip install toolstranslator[server]"
        ) from exc


def _print_check(check: CheckResult) -> None:
    icon = "✔" if check.ok else "✖"
    color = typer.colors.GREEN if check.ok else typer.colors.RED
    typer.secho(f"{icon} {check.name}: {check.details}", fg=color)
    if not check.ok and check.suggestion:
        typer.secho(f"  → Sugerencia: {check.suggestion}", fg=typer.colors.YELLOW)


def _final_summary(checks: list[CheckResult]) -> tuple[str, int]:
    oks = sum(1 for c in checks if c.ok)
    if oks == len(checks):
        return "✔ Listo para usar", 0
    if oks > 0:
        return "⚠ Parcialmente listo", 1
    return "✖ No operativo", 2


@app.command()
def doctor() -> None:
    """Run complete diagnostics like `flutter doctor` style."""
    _ensure_server_extra()
    manager = DockerManager()

    typer.secho("\nToolsTranslator Doctor", bold=True)
    typer.echo("Analizando entorno del servidor de traducción...\n")

    checks = manager.diagnostics()
    for check in checks:
        _print_check(check)

    summary, status = _final_summary(checks)
    typer.echo("")
    if status == 0:
        typer.secho(summary, fg=typer.colors.GREEN, bold=True)
        raise typer.Exit(code=0)
    if status == 1:
        typer.secho(summary, fg=typer.colors.YELLOW, bold=True)
        raise typer.Exit(code=1)
    typer.secho(summary, fg=typer.colors.RED, bold=True)
    raise typer.Exit(code=2)


@app.command()
def install() -> None:
    """Provision and validate LibreTranslate runtime step by step."""
    _ensure_server_extra()
    manager = DockerManager()

    typer.secho("\nToolsTranslator Install", bold=True)

    typer.echo("[1/5] Verificando Docker instalado...")
    if not manager.docker_installed():
        typer.secho("✖ Docker no está instalado o no está en PATH.", fg=typer.colors.RED)
        typer.secho("  → Instala Docker y vuelve a intentar.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=2)
    typer.secho("✔ Docker instalado.", fg=typer.colors.GREEN)

    typer.echo("[2/5] Verificando servicio Docker...")
    if not manager.docker_available():
        typer.secho("✖ Docker daemon no está activo.", fg=typer.colors.RED)
        typer.secho("  → Inicia Docker Desktop/Service y reintenta.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=2)
    typer.secho("✔ Docker daemon activo.", fg=typer.colors.GREEN)

    typer.echo("[3/5] Verificando imagen de LibreTranslate...")
    if not manager.image_exists():
        typer.echo("  Imagen no encontrada, descargando...")
        ok, message = manager.pull_image()
        if not ok:
            typer.secho(f"✖ Error al descargar imagen: {message}", fg=typer.colors.RED)
            typer.secho(
                f"  → Prueba manual: docker pull {manager.image}",
                fg=typer.colors.YELLOW,
            )
            raise typer.Exit(code=2)
        typer.secho("✔ Imagen descargada correctamente.", fg=typer.colors.GREEN)
    else:
        typer.secho("✔ Imagen disponible.", fg=typer.colors.GREEN)

    typer.echo("[4/5] Iniciando contenedor LibreTranslate...")
    ok, message = manager.start_container()
    if not ok:
        typer.secho(f"✖ No se pudo iniciar/crear el contenedor: {message}", fg=typer.colors.RED)
        typer.secho(
            f"  → Revisa logs: docker logs {manager.container_name}",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=2)
    typer.secho(f"✔ Contenedor operativo: {message}", fg=typer.colors.GREEN)

    typer.echo("[5/5] Verificando conectividad del servidor...")
    healthy, details = manager.healthcheck(timeout_s=5)
    if not healthy:
        typer.secho(f"✖ Servicio no accesible: {details}", fg=typer.colors.RED)
        typer.secho(
            f"  → Verifica puertos y logs: docker logs {manager.container_name}",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=2)
    typer.secho(f"✔ {details}", fg=typer.colors.GREEN)

    typer.secho("\n✔ Instalación completada: entorno listo para usar.", fg=typer.colors.GREEN, bold=True)


@app.command()
def status() -> None:
    """Quick status command (resumen breve)."""
    _ensure_server_extra()
    manager = DockerManager()
    running = manager.container_running()
    healthy, details = manager.healthcheck(timeout_s=1.5)
    typer.echo(f"container_running={running}")
    typer.echo(f"api_healthy={healthy}")
    typer.echo(f"details={details}")


@app.command()
def restart() -> None:
    """Restart LibreTranslate container."""
    _ensure_server_extra()
    manager = DockerManager()
    ok, message = manager.restart_container()
    if ok:
        typer.secho(f"✔ {message}", fg=typer.colors.GREEN)
        raise typer.Exit(code=0)
    typer.secho(f"✖ {message}", fg=typer.colors.RED)
    typer.secho(f"  → Ejecuta `toolstranslator install` para recrearlo si es necesario.", fg=typer.colors.YELLOW)
    raise typer.Exit(code=1)


@app.command("clean-server")
def clean_server() -> None:
    """Remove LibreTranslate container (image is preserved)."""
    _ensure_server_extra()
    manager = DockerManager()
    ok, message = manager.remove_container()
    if ok:
        typer.secho(f"✔ {message}", fg=typer.colors.GREEN)
        raise typer.Exit(code=0)
    typer.secho(f"✖ {message}", fg=typer.colors.RED)
    raise typer.Exit(code=1)
