# Tools/toolsets/tools/courier/get_role_capabilities.py
import os
from pathlib import Path
from typing import Dict, Any, List

SKILLS_BASE_DIR = Path("Tools/agents/skills")

def get_role_capabilities() -> Dict[str, Any]:
    """
    Exclusively for the Courier. Returns an overview of all specialists and their 
    atomic task skills to assist in routing decisions.
    """
    capabilities = {}
    
    if not SKILLS_BASE_DIR.exists():
        return {"error": "Skills directory missing."}
        
    for role_dir in SKILLS_BASE_DIR.iterdir():
        if role_dir.is_dir():
            role_name = role_dir.name
            task_skills_dir = role_dir / "tasks_skills"
            
            tasks = []
            if task_skills_dir.exists():
                tasks = [f.stem for f in task_skills_dir.glob("*.md")]
                
            capabilities[role_name] = {
                "tasks": tasks
            }
            
    return {"specialists": capabilities}
