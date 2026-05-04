import typer
from pathlib import Path
from rune.services import module

def update_cmd(
    init: bool = typer.Option(False, "--init", help="Initialize all submodules."),
    recursive: bool = typer.Option(False, "--recursive", help="Recursive update (placeholder).")
):
    """
    Update runemodules based on .runemodules configuration.
    """
    cwd = Path.cwd()
    if not (cwd / ".rune").exists():
        typer.echo("Error: .rune directory not found. Run `rune init` first.", err=True)
        raise typer.Exit(1)
        
    try:
        module.update_modules(cwd, init)
        typer.echo("Modules updated successfully.")
    except Exception as e:
        typer.echo(f"Error updating modules: {e}", err=True)
        raise typer.Exit(1)
