from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Type
from datetime import datetime
from uuid import UUID
import json

class DBModel(BaseModel):
    """Base class for all internal toolkit tables."""
    
    # Type mapping: Python -> DuckDB
    TYPE_MAP = {
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
        for name, field in cls.__fields__.items():
            # Get the base type (handling Optional)
            base_type = field.type_
            db_type = cls.TYPE_MAP.get(base_type, "VARCHAR")
            
            # Special handling for Primary Keys (we assume 'id' or '{model}_id' is PK)
            pk_suffix = ""
            if name.endswith("_id") and (name.startswith(cls.__name__.lower()) or name == "task_id" or name == "event_id"):
                if db_type == "UUID":
                    pk_suffix = " PRIMARY KEY"
                elif db_type == "INTEGER":
                    # For integers we use sequences by default
                    pk_suffix = f" PRIMARY KEY DEFAULT nextval('{schema}.{table}_seq')"

            columns.append(f'"{name}" {db_type}{pk_suffix}')

        # Add Standard timestamps if not already in model
        if "created_at" not in cls.__fields__:
            columns.append('"created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        if "updated_at" not in cls.__fields__:
            columns.append('"updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP')

        # Generate sequence if we have an integer PK
        seq_sql = ""
        if any("nextval" in c for c in columns):
            seq_sql = f"CREATE SEQUENCE IF NOT EXISTS {schema}.{table}_seq;\n"

        cols_str = ",\n    ".join(columns)
        return f"{seq_sql}CREATE TABLE IF NOT EXISTS {schema}.\"{table}\" (\n    {cols_str}\n);"