import hashlib
import duckdb
import os
from loguru import logger
from .vector_manager import VectorManager


class AssetManager:
    def __init__(self, master_db="Data/WoW_Master.duckdb"):
        self.master_db = os.path.abspath(master_db)
        self.vector_manager = VectorManager()
        self._init_db()

    def _init_db(self):
        with duckdb.connect(self.master_db) as conn:
            conn.execute("CREATE SCHEMA IF NOT EXISTS archive")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS archive.assets (
                    content_hash VARCHAR PRIMARY KEY,
                    file_id INTEGER,
                    binary_data BLOB,
                    extension VARCHAR,
                    size_bytes INTEGER,
                    first_seen_build VARCHAR,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Asset Archive initialized in DuckDB.")

    def ingest_asset(self, file_path, file_id, build_version, description=None):
        """Dual-Ingestion: Binary to DuckDB, Metadata/Description to Vector DB."""
        with open(file_path, "rb") as f:
            data = f.read()

        content_hash = hashlib.sha256(data).hexdigest()
        size = len(data)
        ext = os.path.splitext(file_path)[1]

        # 1. DuckDB: Deduplizierter Binär-Speicher
        try:
            with duckdb.connect(self.master_db) as conn:
                # Prüfen ob bereits vorhanden
                exists = conn.execute("SELECT 1 FROM archive.assets WHERE content_hash = ?", [content_hash]).fetchone()
                if not exists:
                    conn.execute(
                        """
                        INSERT INTO archive.assets (content_hash, file_id, binary_data, extension, size_bytes, first_seen_build)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (content_hash, file_id, data, ext, size, build_version),
                    )
                    logger.info(f"Stored new binary asset: {file_id} ({ext})")
                else:
                    logger.info(f"Asset {file_id} already exists (Deduplicated).")
        except Exception as e:
            logger.error(f"Failed to store binary: {e}")
            return None

        # 2. Vector DB: Semantischer Index
        # Wenn kein Modell da ist, nutzen wir Metadaten als Suchtext
        search_text = (
            description or f"WoW Asset FileID {file_id}, Extension {ext}, Size {size} bytes. Build: {build_version}"
        )

        metadata = {
            "content_hash": content_hash,
            "file_id": file_id,
            "extension": ext,
            "build": build_version,
            "type": "asset",
        }

        self.vector_manager.add_memory("Archivist", search_text, metadata)
        return content_hash

    def get_asset(self, content_hash):
        """Holt die Binärdaten aus dem Archiv."""
        with duckdb.connect(self.master_db) as conn:
            res = conn.execute(
                "SELECT binary_data FROM archive.assets WHERE content_hash = ?", [content_hash]
            ).fetchone()
            return res[0] if res else None
