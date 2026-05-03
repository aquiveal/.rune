import subprocess
from pathlib import Path
from typing import List, Optional

def get_value(config_path: Path, key: str) -> Optional[str]:
    """Get a single value from the config file."""
    try:
        result = subprocess.run(
            ["git", "config", "--file", str(config_path), key],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_all(config_path: Path, key: str) -> List[str]:
    """Get all values for a multi-valued key."""
    try:
        result = subprocess.run(
            ["git", "config", "--file", str(config_path), "--get-all", key],
            capture_output=True,
            text=True,
            check=True
        )
        return [line for line in result.stdout.strip().split("\n") if line]
    except subprocess.CalledProcessError:
        return []

def set_value(config_path: Path, key: str, value: str) -> None:
    """Set a single value in the config file."""
    subprocess.run(
        ["git", "config", "--file", str(config_path), key, value],
        check=True
    )

def add(config_path: Path, key: str, value: str) -> None:
    """Add a new line to the option without altering any existing values."""
    subprocess.run(
        ["git", "config", "--file", str(config_path), "--add", key, value],
        check=True
    )

def remove(config_path: Path, key: str) -> None:
    """Remove a key from the config file."""
    subprocess.run(
        ["git", "config", "--file", str(config_path), "--unset-all", key],
        check=True
    )
