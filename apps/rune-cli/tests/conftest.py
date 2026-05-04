import pytest
from pathlib import Path
import subprocess
import shutil

@pytest.fixture
def mock_git_repo(tmp_path):
    repo_path = tmp_path / "mock_repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    
    # Create some content
    skill_dir = repo_path / "skills" / "Automatiq"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Mock Skill")
    
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)
    
    return repo_path
