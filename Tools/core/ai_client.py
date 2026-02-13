import requests
import json
from loguru import logger
from typing import Dict, Any

class AIClient:
    def __init__(self, ollama_url="http://localhost:11434/api/chat", model="qwen3:8b", debug=True, threads=6):
        self.ollama_url = ollama_url
        self.model = model
        self.debug = debug
        self.threads = threads

    def robust_json_decode(self, data):
        """Extracts JSON from common wrapper formats."""
        if not isinstance(data, dict): return {}
        if len(data) == 1:
            key = list(data.keys())[0]
            if isinstance(data[key], dict): return data[key]
        for wrapper in ["analysis", "result", "query_analysis", "discovery", "mapping"]:
            if wrapper in data and isinstance(data[wrapper], dict): return data[wrapper]
        return data

    def ask(self, role: str, prompt: str, temperature: float = 0.1) -> Dict[str, Any]:
        """Bridge to the local LLM via Ollama."""
        if self.debug:
            logger.debug(f"\n{'=' * 80}\n[DEBUG] ROLE: {role}\nPROMPT:\n{prompt}\n{'-' * 80}")
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"You are {role}. Return ONLY raw JSON."},
                {"role": "user", "content": prompt}
            ],
            "stream": False, 
            "format": "json", 
            "options": {"num_thread": self.threads, "temperature": temperature},
        }
        
        try:
            r = requests.post(self.ollama_url, json=payload, timeout=120)
            r.raise_for_status()
            res = r.json()
            content = res["message"]["content"]
            
            if self.debug:
                logger.debug(f"RAW RESPONSE:\n{content}\n{'=' * 80}")
            
            parsed = json.loads(content)
            return self.robust_json_decode(parsed)
            
        except Exception as e:
            logger.error(f"AI Call failed for role '{role}': {e}")
            return {}
