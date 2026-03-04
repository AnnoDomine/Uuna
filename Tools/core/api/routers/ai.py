from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import List, Optional

from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.training.pattern_trainer import run_pattern_training
from Tools.agents.requests.request_librarian import request_librarian
from Tools.core.shared_debugger import debugger

# Imports for training models from centralized file
from Tools.agents.requests.agent_models import (
    SpecialistSelection, LibrarianResponse, SageVerdict, 
    ObserverVerdict, TinkerAssessment, LoreResearchStatus, 
    SecurityAuditStatus
)
from Tools.toolsets.tools.courier.orchestration_helper import DefaultToolSelection

router = APIRouter(prefix="/ai", tags=["ai"])

# Mapping for training
TRAINING_MODELS = {
    Agents.COURIER.value: SpecialistSelection,
    Agents.LIBRARIAN.value: LibrarianResponse,
    Agents.SAGES.value: SageVerdict,
    Agents.OBSERVER.value: ObserverVerdict,
    Agents.TINKER.value: TinkerAssessment,
    Agents.ARCHIVIST.value: DefaultToolSelection,
    Agents.EXPEDITION_GROUP.value: LoreResearchStatus,
    Agents.SENTINEL.value: SecurityAuditStatus
}

class TrainRequest(BaseModel):
    role: str

@router.post("/train")
async def train_ai(req: TrainRequest, background_tasks: BackgroundTasks):
    debugger.add_log(f"Starting AI training for role: {req.role}", agent="API", process="AI:Train")
    if req.role not in TRAINING_MODELS:
        debugger.add_log(f"Training failed: No model for role {req.role}", agent="API", level="ERROR", process="AI:Train")
        raise HTTPException(status_code=400, detail=f"No training model defined for role: {req.role}")
    
    role_enum = Agents(req.role)
    model = TRAINING_MODELS[req.role]
    
    # Run training in background to not block the UI
    background_tasks.add_task(run_pattern_training, role_enum, model)
    
    return {"status": "started", "role": req.role, "model": model.__name__}

class AskRequest(BaseModel):
    prompt: str
    builds: Optional[List[str]] = None


@router.post("/ask")
async def ask_ai(req: AskRequest):
    debugger.add_log(f"AI Request received: {req.prompt[:50]}...", agent="API", process="AI:Ask")
    try:
        # If no builds provided, use a default or empty list (librarian will handle it)
        builds = req.builds if req.builds else []
        
        # request_librarian handles sanitization, RAG, and task spawning
        # Run in threadpool to avoid blocking the API
        result = await run_in_threadpool(request_librarian, req.prompt, builds)
        
        if "error" in result:
            debugger.add_log(f"AI Request error: {result['error']}", agent="API", level="ERROR", process="AI:Ask")
            raise HTTPException(status_code=500, detail=result["error"])
            
        debugger.add_log("AI Request processed successfully.", agent="API", level="SUCCESS", process="AI:Ask")
        return result
    except Exception as e:
        debugger.add_log(f"AI Request crashed: {e}", agent="API", level="ERROR", process="AI:Ask")
        raise HTTPException(status_code=500, detail=str(e))
