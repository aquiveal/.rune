import typer
from pathlib import Path
from rune.services import config

def add_cmd(
    name: str = typer.Argument(...),
    url: str = typer.Argument(...)
):
    """
    Add a new remote repository to .rune/config.
    """
    cwd = Path.cwd()
    rune_config_path = cwd / ".rune" / "config"
    
    if not rune_config_path.exists():
        typer.echo("Error: .rune/config not found. Run `rune init` first.", err=True)
        raise typer.Exit(1)
        
    config.set_value(rune_config_path, f"remote.{name}.url", url)
