from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from Tools.agents.get_agent_skill_set import Agents
from Tools.core.ai_client import AIClient
from Tools.core.security_utils import sanitize_user_prompt
from Tools.agents.training.pattern_trainer import run_pattern_training

# Imports for training models
from Tools.agents.requests.request_courier import SpecialistSelection
from Tools.agents.requests.request_librarian import LibrarianResponse
from Tools.agents.requests.request_sages import SageVerdict
from Tools.agents.requests.request_observer import ObserverVerdict
from Tools.agents.requests.request_tinker import TinkerAssessment
from Tools.toolsets.tools.courier.orchestration_helper import DefaultToolSelection
from Tools.agents.requests.request_expedition_group import LoreResearchStatus
from Tools.agents.requests.request_sentinel import SecurityAuditStatus

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
    if req.role not in TRAINING_MODELS:
        raise HTTPException(status_code=400, detail=f"No training model defined for role: {req.role}")
    
    role_enum = Agents(req.role)
    model = TRAINING_MODELS[req.role]
    
    # Run training in background to not block the UI
    background_tasks.add_task(run_pattern_training, role_enum, model)
    
    return {"status": "started", "role": req.role, "model": model.__name__}

class AskRequest(BaseModel):
    prompt: str


@router.post("/ask")
async def ask_ai(req: AskRequest):
    try:
        # Sanitize user input to prevent prompt injection
        safe_prompt = sanitize_user_prompt(req.prompt)
        
        ai = AIClient()
        # "The Librarian" is the standard role for user interaction in this system
        # Run in threadpool to avoid blocking the event loop (and thus the health check)
        answer = await run_in_threadpool(ai.ask, Agents.LIBRARIAN, safe_prompt)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
