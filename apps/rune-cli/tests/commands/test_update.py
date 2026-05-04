import pytest
from typer.testing import CliRunner
from rune.cli import app
import os
import subprocess

runner = CliRunner()

def test_update_init(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["config", "--add", "agent.name", ".roo"])
    
    # Manually populate .runemodules
    repo_url = str(mock_git_repo).replace('\\', '/')
    runemodules_path = tmp_path / ".runemodules"
    runemodules_path_str = str(runemodules_path).replace('\\', '/')
    
    section = 'runemodule.skills/Automatiq'
    subprocess.run(["git", "config", "--file", runemodules_path_str, f"{section}.path", "skills/Automatiq"], check=True)
    subprocess.run(["git", "config", "--file", runemodules_path_str, f"{section}.url", repo_url], check=True)
    
    # Run update
    result = runner.invoke(app, ["update", "--init"])
    assert result.exit_code == 0
    
    # Check agent dir
    assert (tmp_path / ".roo" / "skills" / "Automatiq" / "SKILL.md").exists()
