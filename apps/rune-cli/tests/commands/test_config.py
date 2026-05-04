import pytest
from typer.testing import CliRunner
from rune.cli import app
import os

runner = CliRunner()

def test_config_set_and_get(tmp_path):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    
    # Set config
    result = runner.invoke(app, ["config", "agent.name", ".roo"])
    assert result.exit_code == 0
    
    # Get config
    result = runner.invoke(app, ["config", "agent.name"])
    assert result.exit_code == 0
    assert ".roo" in result.stdout
    
    # Check .gitignore
    gitignore = tmp_path / ".gitignore"
    assert ".roo/" in gitignore.read_text()

def test_config_add_multiple(tmp_path):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    
    runner.invoke(app, ["config", "--add", "agent.name", ".roo"])
    runner.invoke(app, ["config", "--add", "agent.name", ".cline"])
    
    result = runner.invoke(app, ["config", "--get-all", "agent.name"])
    assert result.exit_code == 0
    assert ".roo" in result.stdout
    assert ".cline" in result.stdout
    
    # Check .gitignore
    gitignore = tmp_path / ".gitignore"
    content = gitignore.read_text()
    assert ".roo/" in content
    assert ".cline/" in content
