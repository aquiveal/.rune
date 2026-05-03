from pathlib import Path

def is_initialized(root_dir: Path) -> bool:
    """Check if the workspace is already initialized."""
    rune_dir = root_dir / ".rune"
    return rune_dir.is_dir()

def init_workspace(root_dir: Path) -> None:
    """
    Initialize the workspace with .rune directory structure,
    .runemodules, and update .gitignore.
    """
    rune_dir = root_dir / ".rune"
    modules_dir = rune_dir / "modules"
    
    # Create directories
    rune_dir.mkdir(exist_ok=True)
    modules_dir.mkdir(exist_ok=True)
    
    # Create empty files
    runemodules_file = root_dir / ".runemodules"
    runemodules_file.touch(exist_ok=True)
    
    config_file = rune_dir / "config"
    config_file.touch(exist_ok=True)
    
    index_file = rune_dir / "index"
    index_file.touch(exist_ok=True)
    
    # Update .gitignore
    _update_gitignore(root_dir)

def _update_gitignore(root_dir: Path) -> None:
    gitignore_file = root_dir / ".gitignore"
    
    content = ""
    if gitignore_file.exists():
        content = gitignore_file.read_text()
        
    ignore_block = "\n# Rune\n.rune/\n" # Will add agents later when configured
    
    if "# Rune" not in content:
        if content and not content.endswith("\n"):
            content += "\n"
        content += ignore_block
        gitignore_file.write_text(content)
