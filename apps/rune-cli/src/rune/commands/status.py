import typer
from pathlib import Path
from rune.services import module

def status_cmd():
    """
    Show status of runemodules.
    """
    cwd = Path.cwd()
    if not (cwd / ".rune").exists():
        typer.echo("Error: .rune directory not found. Run `rune init` first.", err=True)
        raise typer.Exit(1)
        
    status_info = module.get_status(cwd)
    for mod, stat in status_info.items():
        typer.echo(f"{mod}: {stat}")
