import typer
from pathlib import Path
from rune.services import skill

def validate_cmd(
    path: Path = typer.Argument(Path.cwd(), help="Path to the skill directory or SKILL.md file.")
):
    """
    Validate a skill's metadata.
    """
    is_valid, errors, name = skill.validate_skill(path)
    
    if not is_valid:
        typer.echo(f"Error: Validation failed for {path}:", err=True)
        for error in errors:
            typer.echo(f"  - {error}", err=True)
        raise typer.Exit(1)
        
    typer.echo(f"Skill '{name}' is valid!")
