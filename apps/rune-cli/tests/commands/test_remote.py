import pytest
from typer.testing import CliRunner
from rune.cli import app
import os

runner = CliRunner()

def test_remote_add(tmp_path):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    
    result = runner.invoke(app, ["remote", "add", "origin", "https://github.com/my-org/central-rules.git"])
    assert result.exit_code == 0
    
    # Check config
    result = runner.invoke(app, ["config", "remote.origin.url"])
    assert result.exit_code == 0
    assert "https://github.com/my-org/central-rules.git" in result.stdout
