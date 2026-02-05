import requests
from loguru import logger

class EmbeddingHandler:
    def __init__(self, ollama_url="http://localhost:11434/api/embeddings", model="qwen3-embedding:latest"):
        self.ollama_url = ollama_url
        self.model = model

    def get_embedding(self, text: str):
        try:
            payload = {
                "model": self.model,
                "prompt": text
            }
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
