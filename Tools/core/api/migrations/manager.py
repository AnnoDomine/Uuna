import duckdb
from loguru import logger
import os


class MigrationManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.queries_path = "Tools/core/api/queries/migrations"

    def _load_query(self, name: str) -> str:
        with open(os.path.join(self.queries_path, f"{name}.sql"), "r") as f:
            return f.read().strip()

    def initialize_registry(self):
        """Ensures the migrations table exists."""
        sql = self._load_query("init_registry")
        with duckdb.connect(self.db_path) as con:
            for query in sql.split(";"):
                if query.strip():
                    con.execute(query)

    def apply_model(self, model_class):
        """Generates and applies the SQL for a given model, if not already applied."""
        name = model_class.__name__

        # Check if migration was already applied
        with duckdb.connect(self.db_path) as con:
            try:
                res = con.execute("SELECT version FROM registry.migrations WHERE model_name = ?", [name]).fetchone()
                if res:
                    # For now, we assume version 1 is current.
                    # Later we can implement incremental versions.
                    logger.debug(f"Migration for {name} already applied. Skipping.")
                    return
            except Exception:
                pass  # Table might not exist yet, proceed to apply

        sql = model_class.to_sql()
        mark_sql = self._load_query("mark_migration")

        with duckdb.connect(self.db_path) as con:
            try:
                con.execute(sql)
                con.execute(mark_sql, [name, 1])
                logger.info(f"Applied migration for model: {name}")
            except Exception as e:
                logger.error(f"Migration failed for {name}: {e}")
