import re
import yaml
from pathlib import Path
from typing import List, Tuple, Optional

# Validation Constants
SKILL_NAME_MIN_LENGTH = 1
SKILL_NAME_MAX_LENGTH = 64
SKILL_NAME_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DESC_MIN_LENGTH = 1
DESC_MAX_LENGTH = 1024

def validate_skill(path: Path) -> Tuple[bool, List[str], Optional[str]]:
    """
    Validates a skill at the given path.
    Returns (is_valid, errors, skill_name).
    """
    if path.is_dir():
        skill_file = path / "SKILL.md"
    else:
        skill_file = path
        
    if not skill_file.exists():
        return False, [f"SKILL.md not found at {skill_file}"], None

    parent_dir_name = skill_file.parent.name
    errors = []

    try:
        content = skill_file.read_text(encoding="utf-8")
        
        if not content.startswith("---"):
            errors.append("Missing YAML frontmatter (must start with '---')")
            return False, errors, None
            
        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append("Invalid YAML frontmatter format (missing closing '---')")
            return False, errors, None
            
        frontmatter_str = parts[1]
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML syntax in frontmatter: {e}")
            return False, errors, None

        if not isinstance(frontmatter, dict):
            errors.append("Frontmatter must be a YAML dictionary")
            return False, errors, None

        # Validate Name
        name = frontmatter.get("name")
        if not name:
            errors.append("Missing required 'name' field in frontmatter")
        elif not isinstance(name, str):
            errors.append("'name' field must be a string")
        else:
            if len(name) < SKILL_NAME_MIN_LENGTH or len(name) > SKILL_NAME_MAX_LENGTH:
                errors.append(f"Name length must be between {SKILL_NAME_MIN_LENGTH} and {SKILL_NAME_MAX_LENGTH} characters (got {len(name)})")
            
            if not SKILL_NAME_REGEX.match(name):
                errors.append("Name must contain only lowercase letters, numbers, and hyphens. Cannot start/end with a hyphen or have consecutive hyphens.")
                
            if name != parent_dir_name:
                errors.append(f"Name in frontmatter ('{name}') must exactly match the parent directory name ('{parent_dir_name}')")

        # Validate Description
        description = frontmatter.get("description")
        if not description:
            errors.append("Missing required 'description' field in frontmatter")
        elif not isinstance(description, str):
            errors.append("'description' field must be a string")
        else:
            desc_len = len(description.strip())
            if desc_len < DESC_MIN_LENGTH or desc_len > DESC_MAX_LENGTH:
                errors.append(f"Description length must be between {DESC_MIN_LENGTH} and {DESC_MAX_LENGTH} characters (got {desc_len})")

        if errors:
            return False, errors, name
            
        return True, [], name

    except Exception as e:
        return False, [f"Unexpected error reading {skill_file}: {e}"], None
