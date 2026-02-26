from loguru import logger
import os


class MigrationManager:
    def __init__(self, db_client):
        self.db = db_client
        self.queries_path = "Tools/core/api/queries/migrations"

    def _load_query(self, name: str) -> str:
        with open(os.path.join(self.queries_path, f"{name}.sql"), "r") as f:
            return f.read().strip()

    def initialize_registry(self):
        """Ensures the migrations table exists."""
        sql = self._load_query("init_registry")
        for query in sql.split(";"):
            if query.strip():
                self.db.execute(query)

    def apply_model(self, model_class):
        """Generates and applies the SQL for a given model, if not already applied."""
        name = model_class.__name__

        # Check if migration was already applied
        try:
            res = self.db.execute("SELECT version FROM registry.migrations WHERE model_name = ?", [name]).fetchone()
            if res:
                logger.debug(f"Migration for {name} already applied. Skipping.")
                return
        except Exception:
            pass  # Table might not exist yet, proceed to apply

        sql = model_class.to_sql()
        mark_sql = self._load_query("mark_migration")

        try:
            self.db.execute(sql)
            self.db.execute(mark_sql, [name, 1])
            logger.info(f"Applied migration for model: {name}")
        except Exception as e:
            logger.error(f"Migration failed for {name}: {e}")
