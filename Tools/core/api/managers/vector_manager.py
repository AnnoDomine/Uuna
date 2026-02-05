import duckdb
import os
import uuid
import json
from loguru import logger
from .embedding_handler import EmbeddingHandler

class VectorManager:
    def __init__(self, db_path="Data/knowledge/role_memory.duckdb"):
        self.db_path = os.path.abspath(db_path)
        self.embedding_handler = EmbeddingHandler()
        self._init_db()

    def _init_db(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            # Try to initialize. If it's locked, we'll assume it's already initialized.
            try:
                with duckdb.connect(self.db_path) as conn:
                    conn.execute("INSTALL vss; LOAD vss;")
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS memory (
                            id VARCHAR PRIMARY KEY,
                            role VARCHAR,
                            content TEXT,
                            metadata TEXT,
                            embedding FLOAT[4096],
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    logger.info(f"Vector Database initialized at {self.db_path}")
            except Exception as e:
                if "Could not set lock" in str(e):
                    logger.warning(f"Vector DB locked, assuming initialized: {e}")
                else:
                    raise e
        except Exception as e:
            logger.error(f"Failed to initialize Vector DB: {e}")

    def add_memory(self, role: str, content: str, metadata: dict = {}):
        embedding = self.embedding_handler.get_embedding(content)
        if not embedding:
            return None
        
        mem_id = str(uuid.uuid4())
        try:
            with duckdb.connect(self.db_path) as conn:
                conn.execute("INSTALL vss; LOAD vss;")
                conn.execute(
                    "INSERT INTO memory (id, role, content, metadata, embedding) VALUES (?, ?, ?, ?, ?)",
                    (mem_id, role, content, json.dumps(metadata), embedding)
                )
            return mem_id
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return None

    def search_memory(self, role: str, query_text: str, limit: int = 5):
        query_embedding = self.embedding_handler.get_embedding(query_text)
        if not query_embedding:
            return []
        
        try:
            # Use read_only=True for searches to avoid locks
            with duckdb.connect(self.db_path, read_only=True) as conn:
                conn.execute("INSTALL vss; LOAD vss;")
                # Using cosine distance for similarity
                sql = """
                    SELECT content, metadata, array_cosine_similarity(embedding, ?::FLOAT[4096]) as score
                    FROM memory
                    WHERE role = ?
                    ORDER BY score DESC
                    LIMIT ?
                """
                res = conn.execute(sql, [query_embedding, role, limit]).fetchall()
                
                results = []
                for row in res:
                    results.append({
                        "content": row[0],
                        "metadata": json.loads(row[1]),
                        "score": row[2]
                    })
                return results
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []
