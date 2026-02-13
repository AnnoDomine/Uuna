from pydantic import BaseModel
from typing import Dict, Type, ClassVar
from datetime import datetime
from uuid import UUID

class DBModel(BaseModel):
    """Base class for all internal toolkit tables."""
    
    # Type mapping: Python -> DuckDB
    TYPE_MAP: ClassVar[Dict[Type, str]] = {
        str: "VARCHAR",
        int: "INTEGER",
        float: "DOUBLE",
        bool: "BOOLEAN",
        datetime: "TIMESTAMP",
        UUID: "UUID",
        dict: "JSON",
        list: "JSON"
    }

    @classmethod
    def get_table_name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def get_schema(cls) -> str:
        return "research"

    @classmethod
    def to_sql(cls) -> str:
        """Generates the CREATE TABLE statement."""
        schema = cls.get_schema()
        table = cls.get_table_name()
        
        columns = []
        for name, field in cls.model_fields.items():
            # Get the base type
            base_type = field.annotation
            # Handle Optional/Union
            if hasattr(base_type, "__args__"):
                base_type = base_type.__args__[0]
            
            db_type = cls.TYPE_MAP.get(base_type, "VARCHAR")
            
            # Special handling for Primary Keys
            pk_suffix = ""
            # Logic: A column is a PK if it's {model}_id, {table_singular}_id, or just 'id'
            model_prefix = cls.__name__.lower()
            table_prefix = cls.get_table_name().lower().rstrip('s')
            
            is_pk_candidate = (
                name == f"{model_prefix}_id" or 
                name == f"{table_prefix}_id" or 
                name == "id" or
                (name == "task_id" and cls.__name__ == "Task") or
                (name == "event_id" and cls.__name__ == "TaskEvent") or
                (name == "log_id" and cls.__name__ == "EventLog") or
                (name == "score_id" and cls.__name__ == "ScoreBoard")
            )

            if is_pk_candidate:
                if db_type == "UUID":
                    pk_suffix = " PRIMARY KEY"
                elif db_type == "INTEGER":
                    pk_suffix = f" PRIMARY KEY DEFAULT nextval('{schema}.{table}_seq')"

            columns.append(f'"{name}" {db_type}{pk_suffix}')

        # Add Standard timestamps
        if "created_at" not in cls.model_fields:
            columns.append('"created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        if "updated_at" not in cls.model_fields:
            columns.append('"updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP')

        # Generate sequence if we have an integer PK
        seq_sql = ""
        if any("nextval" in c for c in columns):
            seq_sql = f"CREATE SEQUENCE IF NOT EXISTS {schema}.{table}_seq;\n"

        cols_str = ",\n    ".join(columns)
        return f"{seq_sql}CREATE TABLE IF NOT EXISTS {schema}.\"{table}\" (\n    {cols_str}\n);"
