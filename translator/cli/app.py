from __future__ import annotations

import typer

from translator.docker_manager.manager import DockerManager
from translator.exceptions import ExtraNotInstalledError

app = typer.Typer(help="ToolsTranslator CLI")


def _ensure_server_extra() -> None:
    # Typer is installed only with server extra in project metadata.
    # This check provides explicit message if command entrypoint is invoked manually.
    try:
        import typer as _  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise ExtraNotInstalledError(
            "Server commands require extra dependencies. Install: pip install translator[server]"
        ) from exc


@app.command()
def install() -> None:
    """Start LibreTranslate Docker container if needed."""
    _ensure_server_extra()
    manager = DockerManager()
    ok, message = manager.ensure_running()
    if ok:
        typer.secho(f"✅ {message}", fg=typer.colors.GREEN)
        raise typer.Exit(code=0)
    typer.secho(f"❌ {message}", fg=typer.colors.RED)
    raise typer.Exit(code=1)


@app.command()
def doctor() -> None:
    """Run Docker and container diagnostics."""
    _ensure_server_extra()
    manager = DockerManager()
    typer.echo(f"docker_available={manager.docker_available()}")
    typer.echo(f"container_exists={manager.container_exists()}")
    typer.echo(f"container_running={manager.container_running()}")
