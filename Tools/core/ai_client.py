import json
import time
from typing import Any, Dict, Optional

import requests
from loguru import logger

from Tools.agents.get_agent_skill_set import Agents, get_skill_set
from Tools.core.shared_db_instance import db


class AIClient:
    def __init__(self, ollama_url="http://localhost:11434/api/chat", model="qwen3:8b", debug=True):
        self.ollama_url = ollama_url
        self.model = model
        self.debug = debug
        
        # Caching for DB settings
        self._cached_settings: Dict[str, Any] = {}
        self._last_cache_time = 0
        self._cache_ttl = 300  # 5 Minutes

    def _get_setting(self, key: str, default: Any) -> Any:
        """Loads a setting from DB with caching."""
        current_time = time.time()
        
        # Refresh cache if expired
        if current_time - self._last_cache_time > self._cache_ttl:
            self._refresh_settings_cache()
            
        return self._cached_settings.get(key, default)

    def _refresh_settings_cache(self):
        try:
            # Fetch all relevant AI settings at once
            res = db.execute("SELECT key, value FROM registry.settings WHERE key LIKE 'ai_%'").fetchall()
            for row in res:
                key = row[0]
                value = row[1]
                # Try converting to int if possible
                try:
                    self._cached_settings[key] = int(value)
                except ValueError:
                    self._cached_settings[key] = value
            
            self._last_cache_time = time.time()
        except Exception as e:
            logger.warning(f"Failed to refresh AI settings from DB: {e}")

    def make_request(self, payload, role: Agents, temperature: float = 0.1):
        payload["model"] = self.model
        
        # Load dynamic settings
        num_thread = self._get_setting("ai_num_thread", 6)
        num_ctx = self._get_setting("ai_num_ctx", 2048)
        num_gpu = self._get_setting("ai_num_gpu", 0)

        payload["options"] = {
            "num_thread": num_thread,
            "num_ctx": num_ctx,
            "num_gpu": num_gpu,
            "temperature": temperature
        }
        
        try:
            r = requests.post(self.ollama_url, json=payload, timeout=600)
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

    def ask_direct(self, payload: dict, temperature: float = 0.1) -> Dict[str, Any]:
        return self.make_request(payload, temperature)

    def ask(self, role: Agents, prompt: str, temperature: float = 0.1) -> Dict[str, Any]:
        """Bridge to the local LLM via Ollama."""
        if self.debug:
            logger.debug(f"\n{'=' * 80}\n[DEBUG] ROLE: {role}\nPROMPT:\n{prompt}\n{'-' * 80}")

        payload = {
            "messages": [
                {"role": "system", "content": f"You are {role}. Return ONLY raw JSON."},
                {"role": "system", "content": f"SKILLS:\n{get_skill_set(role)}"},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "format": "json",
        }

        return self.make_request(payload, temperature)
