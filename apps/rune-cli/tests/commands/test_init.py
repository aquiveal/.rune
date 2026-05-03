import pytest
from typer.testing import CliRunner
from rune.cli import app
import os
from pathlib import Path

runner = CliRunner()

def test_init_creates_directories_and_files(tmp_path):
    # Change directory to tmp_path
    os.chdir(tmp_path)
    
    print("Commands:", [c.name for c in app.registered_commands])
    
    # Run the init command
    result = runner.invoke(app, ["init"])
    
    print("OUTPUT:", result.output)
    if result.exception:
        print("EXC:", result.exception)

    assert result.exit_code == 0
    assert "Initialized empty Rune repository" in result.stdout
    
    # Check if directories and files are created
    assert (tmp_path / ".rune").is_dir()
    assert (tmp_path / ".rune" / "modules").is_dir()
    assert (tmp_path / ".runemodules").is_file()
    assert (tmp_path / ".rune" / "config").is_file()
    assert (tmp_path / ".rune" / "index").is_file()
    
    # Check if .gitignore is modified
    gitignore = tmp_path / ".gitignore"
    assert gitignore.is_file()
    content = gitignore.read_text()
    assert "# Rune" in content
    assert ".rune/" in content

def test_init_already_initialized(tmp_path):
    os.chdir(tmp_path)
    
    # First init
    runner.invoke(app, ["init"])
    
    # Second init
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0 # Or a warning? The spec says "should warn or gracefully no-op"
    assert "Rune is already initialized" in result.stdout

