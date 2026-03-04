import json
from typing import Any, Dict

import requests

from Tools.agents.get_agent_skill_set import Agents, get_skill_set
from Tools.core.config_manager import get_config
from Tools.core.shared_debugger import debugger


class AIClient:
    def __init__(self, ollama_url="http://localhost:11434/api/chat", model="qwen3:8b", debug=True):
        self.ollama_url = ollama_url
        self.model = model
        self.debug = debug

    def make_request(self, payload, role: Agents, temperature: float = 0.1):
        payload["model"] = self.model
        
        # Load fresh settings from JSON via ConfigManager
        config = get_config()
        
        payload["options"] = {
            "num_thread": config.ai.num_thread,
            "num_ctx": config.ai.num_ctx,
            "num_gpu": config.ai.num_gpu,
            "temperature": temperature
        }
        
        try:
            r = requests.post(self.ollama_url, json=payload, timeout=600)
            r.raise_for_status()
            res = r.json()
            content = res["message"]["content"]

            if self.debug:
                debugger.add_log(f"RAW RESPONSE:\n{content}", agent="AI_CLIENT", level="DEBUG", process="AI:Request")

            parsed = json.loads(content)
            return self.robust_json_decode(parsed)

        except Exception as e:
            debugger.add_log(f"AI Call failed for role '{role}': {e}", agent="AI_CLIENT", level="ERROR", process="AI:Request")
            return {}

    def robust_json_decode(self, data):
        """Extracts JSON from common wrapper formats."""
        if not isinstance(data, dict):
            return {}
        if len(data) == 1:
            key = list(data.keys())[0]
            if isinstance(data[key], dict):
                return data[key]
        for wrapper in ["analysis", "result", "query_analysis", "discovery", "mapping"]:
            if wrapper in data and isinstance(data[wrapper], dict):
                return data[wrapper]
        return data

    def ask_direct(self, payload: dict, temperature: float = 0.1, role: str = "system") -> Dict[str, Any]:
        return self.make_request(payload, role, temperature)

    def ask(self, role: Agents, prompt: str, temperature: float = 0.1) -> Dict[str, Any]:
        """Bridge to the local LLM via Ollama."""
        if self.debug:
            debugger.add_log(f"ROLE: {role} | PROMPT: {prompt[:100]}...", agent="AI_CLIENT", level="DEBUG", process="AI:Ask")

        payload = {
            "messages": [
                {"role": "system", "content": f"You are {role}. Return ONLY raw JSON."},
                {"role": "system", "content": f"SKILLS:\n{get_skill_set(role)}"},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "format": "json",
        }

        return self.make_request(payload, role, temperature)
