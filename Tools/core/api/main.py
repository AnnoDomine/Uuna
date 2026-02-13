from loguru import logger
from fastapi import FastAPI
from .migrations.manager import MigrationManager
from .managers.log_handler import DatabaseLogHandler
from .models.task import Task
from .models.task_event import TaskEvent
from .models.event_log import EventLog
from .models.score_board import ScoreBoard
from .models.build import Build
from .routers import memory, tasks, scoreboard, logs, settings

app = FastAPI(title="Grand Library API")
DB_PATH = 'Data/WoW_Master.duckdb'

# 1. Setup Logging to Database
db_sink = DatabaseLogHandler(DB_PATH, "api")
logger.add(db_sink.write, level="INFO")

# Register routers
app.include_router(memory.router)
app.include_router(tasks.router)
app.include_router(scoreboard.router)
app.include_router(logs.router)
app.include_router(settings.router)

@app.on_event("startup")
async def startup_event():
    # 2. Run Migrations
    mm = MigrationManager(DB_PATH)
    mm.initialize_registry()
    
    # Register all our models
    models = [Task, TaskEvent, EventLog, ScoreBoard, Build]
    for model in models:
        mm.apply_model(model)
    
    logger.info("Library API and Database Schemas are ready.")

@app.get("/health")
async def health():
    return {"status": "online"}
