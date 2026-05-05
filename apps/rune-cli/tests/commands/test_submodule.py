import pytest
from typer.testing import CliRunner
from rune.cli import app
import os
import subprocess

runner = CliRunner()

def test_submodule_add(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["config", "--add", "agent.name", ".roo"])
    
    repo_url = str(mock_git_repo).replace('\\', '/')
    result = runner.invoke(app, ["submodule", "add", repo_url, "skills/Automatiq"])
    
    assert result.exit_code == 0
    
    # Check .runemodules
    assert (tmp_path / ".runemodules").exists()
    content = (tmp_path / ".runemodules").read_text()
    assert '[runemodule "skills/Automatiq"]' in content
    
def test_submodule_deinit(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["config", "--add", "agent.name", ".roo"])
    
    repo_url = str(mock_git_repo).replace('\\', '/')
    runner.invoke(app, ["submodule", "add", repo_url, "skills/Automatiq"])
    
    # Deinit
    result = runner.invoke(app, ["submodule", "deinit", "skills/Automatiq"])
    assert result.exit_code == 0
    
    # Check .runemodules entry STILL exists
    content = (tmp_path / ".runemodules").read_text()
    assert '[runemodule "skills/Automatiq"]' in content
    
    # Check internal store is removed
    assert not (tmp_path / ".rune" / "modules" / "skills" / "Automatiq").exists()
    
    # Check agent dir is removed
    assert not (tmp_path / ".roo" / "skills" / "Automatiq").exists()

def test_submodule_rm(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["config", "--add", "agent.name", ".roo"])
    
    repo_url = str(mock_git_repo).replace('\\', '/')
    runner.invoke(app, ["submodule", "add", repo_url, "skills/Automatiq"])
    
    # Rm
    result = runner.invoke(app, ["submodule", "rm", "skills/Automatiq"])
    assert result.exit_code == 0
    
    # Check .runemodules entry is gone
    content = (tmp_path / ".runemodules").read_text()
    assert '[runemodule "skills/Automatiq"]' not in content

def test_submodule_add_with_remote_shorthand(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["config", "--add", "agent.name", ".roo"])
    
    repo_url = str(mock_git_repo).replace('\\', '/')
    
    # 1. Add remote
    runner.invoke(app, ["remote", "add", "central", repo_url])
    
    # 2. Add submodule using remote shorthand
    result = runner.invoke(app, ["submodule", "add", "central", "skills/Automatiq"])
    
    assert result.exit_code == 0
    
    # Check .runemodules
    assert (tmp_path / ".runemodules").exists()
@pytest.fixture
def mock_git_repo_with_submodule(tmp_path):
    # 1. Create a submodule repo
    sub_repo_path = tmp_path / "sub_repo"
    sub_repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=sub_repo_path, check=True)
    (sub_repo_path / "data.txt").write_text("submodule data")
    subprocess.run(["git", "add", "."], cwd=sub_repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Submodule initial commit"], cwd=sub_repo_path, check=True)
    
    # 2. Create the main repo
    main_repo_path = tmp_path / "main_repo"
    main_repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=main_repo_path, check=True)
    
    # Add a regular file
    skill_dir = main_repo_path / "skills" / "plasmo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Plasmo Skill")
    
    # Add the submodule
    sub_repo_url = str(sub_repo_path).replace('\\', '/')
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always", "submodule", "add", sub_repo_url, "skills/plasmo/modules"],
        cwd=main_repo_path,
        check=True
    )
    
    subprocess.run(["git", "add", "."], cwd=main_repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Main repo initial commit with submodule"], cwd=main_repo_path, check=True)
    
    return main_repo_path

def test_submodule_add_with_nested_submodule(tmp_path, mock_git_repo_with_submodule):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["config", "--add", "agent.name", ".roo"])
    
    repo_url = str(mock_git_repo_with_submodule).replace('\\', '/')
    result = runner.invoke(app, ["submodule", "add", repo_url, "skills/plasmo"])
    
    assert result.exit_code == 0
    
    # Check if SKILL.md exists
    assert (tmp_path / ".roo" / "skills" / "plasmo" / "SKILL.md").exists()
    
    # Check if nested submodule content exists
    # This proves that the submodule was correctly initialized and copied
    assert (tmp_path / ".roo" / "skills" / "plasmo" / "modules" / "data.txt").exists()
    assert (tmp_path / ".roo" / "skills" / "plasmo" / "modules" / "data.txt").read_text() == "submodule data"
