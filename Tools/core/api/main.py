from fastapi import FastAPI
from loguru import logger

from .managers.log_handler import DatabaseLogHandler
from .migrations.manager import MigrationManager
from .models.build import Build
from .models.event_log import EventLog
from .models.score_board import ScoreBoard
from .models.task import Task
from .models.task_event import TaskEvent
from .routers import ai, builds, logs, memory, scoreboard, settings, tasks
from Tools.core.shared_db_instance import db

app = FastAPI(title="Grand Library API")

# 1. Setup Logging to Database via DB Service (to avoid locks)
db_sink = DatabaseLogHandler(db, "api")
logger.add(db_sink.write, level="INFO")

# Register routers
app.include_router(memory.router)
app.include_router(tasks.router)
app.include_router(scoreboard.router)
app.include_router(logs.router)
app.include_router(settings.router)
app.include_router(ai.router)
app.include_router(builds.router)


@app.on_event("startup")
async def startup_event():
    # 2. Run Migrations via DB Service
    mm = MigrationManager(db)
    mm.initialize_registry()

    # Register all our models
    models = [Task, TaskEvent, EventLog, ScoreBoard, Build]
    for model in models:
        mm.apply_model(model)

    logger.info("Library API and Database Schemas are ready.")


@app.get("/health")
async def health():
    return {"status": "online"}
