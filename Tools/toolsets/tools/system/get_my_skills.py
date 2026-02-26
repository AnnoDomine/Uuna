# Tools/toolsets/tools/system/get_my_skills.py
from pathlib import Path
from typing import Any, Dict

SKILLS_BASE_DIR = Path("Tools/agents/skills")


def get_my_skills(role: str) -> Dict[str, Any]:
    """
    Retrieves the skill-set and instructions for the calling agent.

    Args:
    - role: The role name of the agent (e.g. 'Librarian').
    """
    role_dir = SKILLS_BASE_DIR / role.lower().replace(" ", "_")
    skills_file = role_dir / "SKILLS.md"

    if not skills_file.exists():
        return {"error": f"No skill-set found for role: {role}", "role": role}

    try:
        with open(skills_file, "r") as f:
            content = f.read()

        # Also list available task skills for reference
        task_skills_dir = role_dir / "tasks_skills"
        task_skills = []
        if task_skills_dir.exists():
            task_skills = [f.stem for f in task_skills_dir.glob("*.md")]

        return {"role": role, "master_skills_content": content, "available_tasks": task_skills, "path": str(role_dir)}
    except Exception as e:
        return {"error": str(e), "role": role}
