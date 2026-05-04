import typer
from typing import Optional
from pathlib import Path
from rune.services import config

def config_cmd(
    key: str = typer.Argument(...),
    value: Optional[str] = typer.Argument(None),
    add: bool = typer.Option(False, "--add", help="Add a new line to the option without altering any existing values."),
    get_all: bool = typer.Option(False, "--get-all", help="Get all values for a multi-valued key.")
):
    """
    Get or set options in .rune/config
    """
    cwd = Path.cwd()
    rune_config_path = cwd / ".rune" / "config"
    
    if not rune_config_path.exists():
        typer.echo("Error: .rune/config not found. Run `rune init` first.", err=True)
        raise typer.Exit(1)
        
    if get_all:
        values = config.get_all(rune_config_path, key)
        for v in values:
            typer.echo(v)
        return
        
    if value is not None:
        if add:
            config.add(rune_config_path, key, value)
        else:
            config.set_value(rune_config_path, key, value)
            
        if key == "agent.name":
            from rune.services import workspace
            workspace.update_gitignore(cwd)
    else:
        # Get value
        val = config.get_value(rune_config_path, key)
        if val is not None:
            typer.echo(val)
        else:
            raise typer.Exit(1)
