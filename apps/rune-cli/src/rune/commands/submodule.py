import typer
from pathlib import Path
from rune.services import module

def add_cmd(
    url: str = typer.Argument(..., help="URL of the remote repository."),
    path: str = typer.Argument(..., help="Path within the repository to add as a runemodule.")
):
    """
    Add a new runemodule (Consumer Workflow).
    """
    cwd = Path.cwd()
    if not (cwd / ".rune").exists():
        typer.echo("Error: .rune directory not found. Run `rune init` first.", err=True)
        raise typer.Exit(1)
        
    try:
        module.add_module(cwd, url, path)
        typer.echo(f"Added runemodule '{path}' from '{url}'.")
    except Exception as e:
        typer.echo(f"Error adding runemodule: {e}", err=True)
        raise typer.Exit(1)

def deinit_cmd(
    path: str = typer.Argument(..., help="Path within the repository to deinitialize.")
):
    """
    Deinitialize a runemodule (removes local files but keeps .runemodules entry).
    """
    cwd = Path.cwd()
    if not (cwd / ".rune").exists():
        typer.echo("Error: .rune directory not found. Run `rune init` first.", err=True)
        raise typer.Exit(1)
        
    try:
        module.deinit_module(cwd, path)
        typer.echo(f"Deinitialized runemodule '{path}'.")
    except Exception as e:
        typer.echo(f"Error deinitializing runemodule: {e}", err=True)
        raise typer.Exit(1)

def rm_cmd(
    path: str = typer.Argument(..., help="Path within the repository to remove.")
):
    """
    Remove a runemodule.
    """
    cwd = Path.cwd()
    if not (cwd / ".rune").exists():
        typer.echo("Error: .rune directory not found. Run `rune init` first.", err=True)
        raise typer.Exit(1)
        
    try:
        module.remove_module(cwd, path)
        typer.echo(f"Removed runemodule '{path}'.")
    except Exception as e:
        typer.echo(f"Error removing runemodule: {e}", err=True)
        raise typer.Exit(1)
