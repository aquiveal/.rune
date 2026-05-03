import pytest
from typer.testing import CliRunner
from rune.cli import app
import os
import subprocess
import shutil
import stat

runner = CliRunner()

def rmtree_onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.
    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def test_vendor_add_happy_path(tmp_path, mock_git_repo):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    os.chdir(workspace)
    subprocess.run(["git", "init"], check=True)
    repo_url = "file:///" + str(mock_git_repo).replace('\\', '/')
    subprocess.run(["git", "config", "protocol.file.allow", "always"], check=True)
    
    result = runner.invoke(app, ["vendor", "add", repo_url])
    assert result.exit_code == 0
    assert "Successfully added vendor submodule" in result.output
    
    wrapper_dir = workspace / "mock_repo"
    assert wrapper_dir.exists()
    assert (wrapper_dir / "SKILL.md").exists()
    assert (wrapper_dir / "modules").exists()

def test_vendor_add_intact_state(tmp_path, mock_git_repo):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    os.chdir(workspace)
    subprocess.run(["git", "init"], check=True)
    repo_url = "file:///" + str(mock_git_repo).replace('\\', '/')
    subprocess.run(["git", "config", "protocol.file.allow", "always"], check=True)
    
    # First add
    runner.invoke(app, ["vendor", "add", repo_url])
    
    # Second add
    result = runner.invoke(app, ["vendor", "add", repo_url])
    assert result.exit_code == 0
    assert "is already installed and exists on disk" in result.output

def test_vendor_add_dirty_state_cleanup(tmp_path, mock_git_repo):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    os.chdir(workspace)
    subprocess.run(["git", "init"], check=True)
    repo_url = "file:///" + str(mock_git_repo).replace('\\', '/')
    subprocess.run(["git", "config", "protocol.file.allow", "always"], check=True)
    
    # First add
    runner.invoke(app, ["vendor", "add", repo_url])
    
    # Programmatically simulate user deletion
    wrapper_dir = workspace / "mock_repo"
    shutil.rmtree(wrapper_dir, onerror=rmtree_onerror)
    
    # Second add (dirty state)
    result = runner.invoke(app, ["vendor", "add", repo_url])
    assert result.exit_code == 0
    assert "Detected stale git index" in result.output
    assert "Successfully added vendor submodule" in result.output
    
    # Verify it re-added properly
    assert wrapper_dir.exists()
    assert (wrapper_dir / "modules").exists()
    
    # Verify it re-added properly
    assert wrapper_dir.exists()
    assert (wrapper_dir / "modules").exists()
