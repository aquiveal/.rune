import subprocess
import shutil
import uuid
import sys
from pathlib import Path
from rune.services import config
import os
import re

def add_module(root_dir: Path, url: str, path: str) -> None:
    rune_dir = root_dir / ".rune"
    
    # 0. Resolve shorthand URL from .rune/config if it exists
    resolved_url = config.get_value(rune_dir / "config", f"remote.{url}.url")
    if resolved_url:
        url = resolved_url

    # 1. Fetch target repository into .rune/tmp/
    tmp_dir = rune_dir / "tmp" / str(uuid.uuid4())
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    # Clone with depth 1
    subprocess.run(["git", "clone", "--depth", "1", url, str(tmp_dir)], check=True)
    
    # Find and initialize submodules that are within or at the requested path
    normalized_path = path.replace('\\', '/')
    submodule_paths = []
    gitmodules_file = tmp_dir / ".gitmodules"
    if gitmodules_file.exists():
        result = subprocess.run(
            ["git", "config", "--file", ".gitmodules", "--get-regexp", "path"],
            cwd=str(tmp_dir),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if not line: continue
                parts = line.split(None, 1)
                if len(parts) == 2:
                    sm_path = parts[1].strip()
                    if sm_path == normalized_path or sm_path.startswith(f"{normalized_path}/"):
                        submodule_paths.append(sm_path)
    
    # Always include the requested path to maintain original behavior
    if normalized_path not in submodule_paths:
        submodule_paths.append(normalized_path)

    try:
        # Initialize and update submodules. We remove --depth 1 to be more robust.
        subprocess.run(
            ["git", "-c", "protocol.file.allow=always", "submodule", "update", "--init", "--recursive", "--"] + submodule_paths,
            cwd=str(tmp_dir),
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to initialize submodules in {path}: {e}", file=sys.stderr)
    
    # 2. Extract target directory into .rune/modules/<path>
    source_path = tmp_dir / path
    if not source_path.exists():
        # Clean up
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise FileNotFoundError(f"Path '{path}' not found in remote repository.")
        
    target_path = rune_dir / "modules" / path
    if target_path.exists():
        shutil.rmtree(target_path, ignore_errors=True)
    
    # Copy from tmp to target, ignoring .git files/directories
    shutil.copytree(source_path, target_path, ignore=shutil.ignore_patterns('.git'), symlinks=True)
    
    # Cleanup tmp
    shutil.rmtree(tmp_dir, ignore_errors=True)
    
    # 3. Check out to agents
    agents = config.get_all(rune_dir / "config", "agent.name")
    for agent in agents:
        agent_path = root_dir / agent / path
        if agent_path.exists():
            if agent_path.is_symlink():
                agent_path.unlink()
            else:
                shutil.rmtree(agent_path, ignore_errors=True)
                
        agent_path.parent.mkdir(parents=True, exist_ok=True)
        # Try to symlink first, if fails on Windows without privilege, fallback to copytree
        try:
            os.symlink(target_path.absolute(), agent_path.absolute(), target_is_directory=True)
        except OSError:
            shutil.copytree(target_path, agent_path, symlinks=True)
            
    # 4. Write new entry to .runemodules
    runemodules_path = root_dir / ".runemodules"
    runemodules_path_str = str(runemodules_path).replace('\\', '/')
    # Using git config
    section = f'runemodule.{path}'
    subprocess.run(["git", "config", "--file", runemodules_path_str, f"{section}.path", path], check=True)
    subprocess.run(["git", "config", "--file", runemodules_path_str, f"{section}.url", url], check=True)

def deinit_module(root_dir: Path, path: str) -> None:
    rune_dir = root_dir / ".rune"
    
    # 1. Delete internal store
    target_path = rune_dir / "modules" / path
    if target_path.exists():
        shutil.rmtree(target_path, ignore_errors=True)
        
    # 2. Remove symlinks/copies from agent directories
    agents = config.get_all(rune_dir / "config", "agent.name")
    for agent in agents:
        agent_path = root_dir / agent / path
        if agent_path.exists():
            if agent_path.is_symlink():
                agent_path.unlink()
            else:
                shutil.rmtree(agent_path, ignore_errors=True)

def remove_module(root_dir: Path, path: str) -> None:
    # 1. Deinit module
    deinit_module(root_dir, path)
    
    # 2. Remove entry from .runemodules
    runemodules_path = root_dir / ".runemodules"
    if runemodules_path.exists():
        runemodules_path_str = str(runemodules_path).replace('\\', '/')
        section = f'runemodule.{path}'
        try:
            subprocess.run(["git", "config", "--file", runemodules_path_str, "--remove-section", section], check=True)
        except subprocess.CalledProcessError:
            pass # Section might not exist

def update_modules(root_dir: Path, init: bool = False) -> None:
    """Read .runemodules and add them if missing or initialized."""
    runemodules_path = root_dir / ".runemodules"
    if not runemodules_path.exists():
        return
        
    runemodules_path_str = str(runemodules_path).replace('\\', '/')
    try:
        result = subprocess.run(["git", "config", "--file", runemodules_path_str, "--list"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return
        
    modules = {}
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        key, value = line.split('=', 1)
        if key.startswith('runemodule.'):
            # runemodule.skills/automatiq.path -> skills/automatiq
            parts = key.split('.')
            if len(parts) >= 3:
                mod_path = '.'.join(parts[1:-1])
                prop = parts[-1]
                if mod_path not in modules:
                    modules[mod_path] = {}
                modules[mod_path][prop] = value
                
    for mod_path, props in modules.items():
        if 'url' in props and 'path' in props:
            # Re-add/update the module
            # We are using add_module which effectively updates it
            add_module(root_dir, props['url'], props['path'])

def get_status(root_dir: Path) -> dict:
    """Check status of modules in .runemodules"""
    rune_dir = root_dir / ".rune"
    runemodules_path = root_dir / ".runemodules"
    status = {}
    if not runemodules_path.exists():
        return status
        
    runemodules_path_str = str(runemodules_path).replace('\\', '/')
    try:
        result = subprocess.run(["git", "config", "--file", runemodules_path_str, "--list"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return status
        
    modules = set()
    for line in result.stdout.strip().split('\n'):
        if line.startswith('runemodule.'):
            parts = line.split('=')[0].split('.')
            if len(parts) >= 3:
                modules.add('.'.join(parts[1:-1]))
                
    agents = config.get_all(rune_dir / "config", "agent.name")
    
    for mod in modules:
        stat = "OK"
        if not (rune_dir / "modules" / mod).exists():
            stat = "Missing"
        else:
            for agent in agents:
                if not (root_dir / agent / mod).exists():
                    stat = f"Missing in {agent}"
                    break
        status[mod] = stat
        
    return status
