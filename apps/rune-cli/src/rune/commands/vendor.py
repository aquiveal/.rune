import typer
from pathlib import Path
import subprocess
import shutil
import os

def clean_git_submodule_cache(modules_dir: Path, modules_rel: str):
    try:
        # Remove from git cache forcibly to avoid issues with unstaged .gitmodules
        subprocess.run(["git", "rm", "--cached", "-f", "-r", modules_rel], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        pass

    # Remove the internal git modules directory if it exists
    # Find git root
    try:
        git_root_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], 
            check=True, capture_output=True, text=True
        )
        git_root = Path(git_root_result.stdout.strip())
        
        # Submodule path in .git/modules is based on its path relative to git root
        submodule_git_rel = modules_dir.resolve().relative_to(git_root.resolve()).as_posix()
        internal_git_module_path = git_root / ".git" / "modules" / submodule_git_rel
        
        if internal_git_module_path.exists():
            import stat
            def rmtree_onerror(func, path, exc_info):
                os.chmod(path, stat.S_IWUSR)
                func(path)
            shutil.rmtree(internal_git_module_path, onerror=rmtree_onerror)
            
        # Also clean up .gitmodules
        gitmodules_path = git_root / ".gitmodules"
        if gitmodules_path.exists():
            subprocess.run(["git", "config", "--file", str(gitmodules_path), "--remove-section", f"submodule.{submodule_git_rel}"], capture_output=True)
    except subprocess.CalledProcessError as e:
        pass
    except ValueError as e:
        pass

def add_cmd(
    url: str = typer.Argument(..., help="URL of the remote repository to add as a submodule.")
):
    """
    Add a git submodule for publisher workflows (Vendor).
    """
    cwd = Path.cwd()
    
    # Extract name from URL
    # e.g., https://github.com/my-org/Automatiq.git -> Automatiq
    clean_url = url.rstrip('/')
    repo_name = clean_url.split('/')[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
        
    wrapper_dir = cwd / repo_name
    
    modules_dir = wrapper_dir / "modules"
    modules_rel = modules_dir.relative_to(cwd).as_posix()
    
    # Check state before proceeding
    try:
        git_root_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], 
            check=True, capture_output=True, text=True
        )
        git_root = Path(git_root_result.stdout.strip())
        submodule_git_rel = modules_dir.resolve().relative_to(git_root.resolve()).as_posix()
        internal_git_module_path = git_root / ".git" / "modules" / submodule_git_rel
        has_git_cache = internal_git_module_path.exists()
    except (subprocess.CalledProcessError, ValueError):
        has_git_cache = False
        git_root = cwd

    on_disk = modules_dir.exists() and any(modules_dir.iterdir()) if modules_dir.exists() else False

    if has_git_cache and on_disk:
        typer.echo(f"Submodule '{modules_rel}' is already installed and exists on disk.", err=True)
        raise typer.Exit(0)
    elif has_git_cache and not on_disk:
        typer.echo(f"Detected stale git index for '{modules_rel}'. Cleaning up cache...")
        clean_git_submodule_cache(modules_dir, modules_rel)

    wrapper_dir.mkdir(parents=True, exist_ok=True)
    
    # Boilerplate SKILL.md
    skill_md = wrapper_dir / "SKILL.md"
    if not skill_md.exists():
        skill_md.write_text(f"# {repo_name}\n\n> [!NOTE] Agent Context: The source code for this skill is co-located in the modules/ directory.\n")
    
    try:
        subprocess.run(["git", "-c", "protocol.file.allow=always", "submodule", "add", url, modules_rel], check=True)
        typer.echo(f"Successfully added vendor submodule {url} into {modules_rel}")
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error: Git failed to add the vendor submodule (exit code {e.returncode}). See Git's output above for details.", err=True)
        raise typer.Exit(1)
