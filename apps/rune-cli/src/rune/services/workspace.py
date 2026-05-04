from pathlib import Path

def is_initialized(root_dir: Path) -> bool:
    """Check if the workspace is already initialized."""
    rune_dir = root_dir / ".rune"
    return rune_dir.is_dir()

def update_gitignore(root_dir: Path) -> None:
    from rune.services import config
    
    gitignore_file = root_dir / ".gitignore"
    
    content = ""
    if gitignore_file.exists():
        content = gitignore_file.read_text()
        
    lines = content.splitlines()
    
    entries_to_add = [".rune/"]
    rune_dir = root_dir / ".rune"
    config_file = rune_dir / "config"
    if config_file.exists():
        agents = config.get_all(config_file, "agent.name")
        for agent in agents:
            entries_to_add.append(f"{agent}/")
            
    missing_entries = [entry for entry in entries_to_add if entry not in lines and entry.strip('/') not in lines]
    
    if missing_entries:
        if content and not content.endswith("\n"):
            content += "\n"
            
        if "# Rune" not in lines:
            content += "\n# Rune\n"
            
        for entry in missing_entries:
            content += f"{entry}\n"
            
        gitignore_file.write_text(content)

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
    update_gitignore(root_dir)
