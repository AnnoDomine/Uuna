import json
import os
from typing import Dict

from pydantic import BaseModel, Field, field_validator

from Tools.core.shared_debugger import debugger

SETTINGS_PATH = "Tools/web/react-node/src/app/settings.json"


class AISettings(BaseModel):
    num_thread: int = Field(default=6, ge=1, le=128)
    num_ctx: int = Field(default=2048, ge=512, le=32768)
    num_gpu: int = Field(default=0, ge=0, le=200)
    acceleration_mode: str = Field(default="cpu")
    memory_limit: int = Field(default=3, ge=1, le=20)

    @field_validator("acceleration_mode")
    @classmethod
    def validate_mode(cls, v):
        if v not in ["cpu", "gpu", "auto"]:
            raise ValueError("acceleration_mode must be 'cpu', 'gpu' or 'auto'")
        return v


class IngestionSettings(BaseModel):
    workers: int = Field(default=4, ge=1, le=32)
    threads: int = Field(default=4, ge=1, le=64)
    limit_per_build: int = Field(default=0, ge=0)
    sync_builds_on_startup: bool = True


class AnalysisSettings(BaseModel):
    use_global_mapping: bool = True
    auto_skip_unidentifiable: bool = False


class SystemSettings(BaseModel):
    debug: bool = True
    localisation: str = "german"
    ui_theme: str = "dark"
    cooldown: float = Field(default=1.0, ge=0.0)


class TasksSettings(BaseModel):
    max_events_total: int = Field(default=80, ge=1, le=500)
    max_tries_archivist: int = Field(default=6, ge=1, le=500)
    max_tries_cartorapher: int = Field(default=3, ge=1, le=500)
    max_tries_expedition_group: int = Field(default=5, ge=1, le=500)
    max_tries_sentinel: int = Field(default=3, ge=1, le=500)


class AppConfig(BaseModel):
    ai: AISettings = AISettings()
    ingestion: IngestionSettings = IngestionSettings()
    analysis: AnalysisSettings = AnalysisSettings()
    system: SystemSettings = SystemSettings()
    tasks: TasksSettings = TasksSettings()


class ConfigManager:
    @staticmethod
    def get_structure() -> Dict[str, list]:
        """Dynamically generates the structure from the AppConfig class."""
        structure = {}
        # Pydantic V2 uses model_fields
        for field_name, field in AppConfig.model_fields.items():
            # Get the nested model class from the field annotation
            sub_model = field.annotation
            if hasattr(sub_model, "model_fields"):
                structure[field_name] = list(sub_model.model_fields.keys())
        return structure

    @staticmethod
    def load_config() -> AppConfig:
        """Reads and validates the settings from JSON file. Always read fresh."""
        if not os.path.exists(SETTINGS_PATH):
            debugger.add_log(
                f"Settings file {SETTINGS_PATH} missing. Creating default.",
                agent="CORE",
                level="WARNING",
                process="Config:Load",
            )
            ConfigManager.save_config(AppConfig())
            return AppConfig()

        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AppConfig(**data)
        except Exception as e:
            debugger.add_log(
                f"Failed to load or validate config: {e}. Falling back to defaults.",
                agent="CORE",
                level="ERROR",
                process="Config:Load",
            )
            return AppConfig()

    @staticmethod
    def save_config(config: AppConfig):
        """Saves the validated config to the JSON file."""
        try:
            os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                # Pydantic V2 uses model_dump
                json.dump(config.model_dump(), f, indent=4)
        except Exception as e:
            debugger.add_log(f"Failed to save config: {e}", agent="CORE", level="ERROR", process="Config:Save")


# Global Accessor
def get_config() -> AppConfig:
    return ConfigManager.load_config()
