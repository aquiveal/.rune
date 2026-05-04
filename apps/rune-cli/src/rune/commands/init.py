import typer
from pathlib import Path
from rune.services import workspace

def init_cmd():
    """
    Initialize a new Rune repository.
    """
    cwd = Path.cwd()
    if workspace.is_initialized(cwd):
        typer.echo("Rune is already initialized in this directory.")
        return

    workspace.init_workspace(cwd)
    typer.echo("Initialized empty Rune repository")
