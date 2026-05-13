import pytest
from pathlib import Path
from rune.services.skill import validate_skill

def test_validate_skill_valid(tmp_path):
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: test-skill\ndescription: A valid test skill\n---\n", encoding="utf-8")
    
    is_valid, errors, name = validate_skill(skill_dir)
    
    assert is_valid is True
    assert not errors
    assert name == "test-skill"

def test_validate_skill_missing_file(tmp_path):
    skill_dir = tmp_path / "empty-skill"
    skill_dir.mkdir()
    
    is_valid, errors, name = validate_skill(skill_dir)
    
    assert is_valid is False
    assert any("SKILL.md not found" in e for e in errors)

def test_validate_skill_missing_frontmatter(tmp_path):
    skill_dir = tmp_path / "no-frontmatter"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("Just some text without frontmatter", encoding="utf-8")
    
    is_valid, errors, name = validate_skill(skill_dir)
    
    assert is_valid is False
    assert any("Missing YAML frontmatter" in e for e in errors)

def test_validate_skill_invalid_yaml(tmp_path):
    skill_dir = tmp_path / "invalid-yaml"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: [unclosed list\n---\n", encoding="utf-8")
    
    is_valid, errors, name = validate_skill(skill_dir)
    
    assert is_valid is False
    assert any("Invalid YAML syntax" in e for e in errors)

def test_validate_skill_name_mismatch(tmp_path):
    skill_dir = tmp_path / "actual-name"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: mismatched-name\ndescription: Valid desc\n---\n", encoding="utf-8")
    
    is_valid, errors, name = validate_skill(skill_dir)
    
    assert is_valid is False
    assert any("must exactly match the parent directory name" in e for e in errors)

def test_validate_skill_invalid_name_format(tmp_path):
    skill_dir = tmp_path / "Invalid_Name"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: Invalid_Name\ndescription: Valid desc\n---\n", encoding="utf-8")
    
    is_valid, errors, name = validate_skill(skill_dir)
    
    assert is_valid is False
    assert any("Name must contain only lowercase letters" in e for e in errors)

def test_validate_skill_missing_fields(tmp_path):
    skill_dir = tmp_path / "missing-fields"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: missing-fields\n---\n", encoding="utf-8")
    
    is_valid, errors, name = validate_skill(skill_dir)
    
    assert is_valid is False
    assert any("Missing required 'description' field" in e for e in errors)

def test_validate_skill_description_length(tmp_path):
    skill_dir = tmp_path / "long-desc"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    long_desc = "a" * 1025
    skill_file.write_text(f"---\nname: long-desc\ndescription: {long_desc}\n---\n", encoding="utf-8")
    
    is_valid, errors, name = validate_skill(skill_dir)
    
    assert is_valid is False
    assert any("Description length must be between" in e for e in errors)
