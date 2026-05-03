import pytest
from typer.testing import CliRunner
from rune.cli import app
import os
import shutil

runner = CliRunner()

def test_status(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["config", "--add", "agent.name", ".roo"])
    
    repo_url = str(mock_git_repo).replace('\\', '/')
    runner.invoke(app, ["submodule", "add", repo_url, "skills/Automatiq"])
    
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "skills/Automatiq: OK" in result.stdout
    
    # Remove from agent dir
    shutil.rmtree(tmp_path / ".roo" / "skills" / "Automatiq")
    result = runner.invoke(app, ["status"])
    assert "skills/Automatiq: Missing in .roo" in result.stdout
