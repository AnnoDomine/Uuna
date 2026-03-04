from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Setup Logging to Database via DB Service (to avoid locks)
    db_sink = DatabaseLogHandler(db, "api")
    logger.add(db_sink.write, level="INFO")

    # 2. Run Migrations via DB Service
    mm = MigrationManager(db)
    mm.initialize_registry()

    # Register all our models
    models = [Task, TaskEvent, EventLog, ScoreBoard, Build]
    for model in models:
        mm.apply_model(model)

    logger.info("Library API and Database Schemas are ready.")
    
    yield

app = FastAPI(title="Grand Library API", lifespan=lifespan)

# CORS configuration for local frontend access
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://0.0.0.0:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(memory.router)
app.include_router(tasks.router)
app.include_router(scoreboard.router)
app.include_router(logs.router)
app.include_router(settings.router)
app.include_router(ai.router)
app.include_router(builds.router)

@app.get("/health")
async def health():
    return {
        "status": "online",
        "service": "Grand Library API (Orchestra)",
        "db_connected": db is not None
    }
