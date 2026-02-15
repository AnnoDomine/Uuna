from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from Tools.agents.get_agent_skill_set import Agents
from Tools.core.ai_client import AIClient

router = APIRouter(prefix="/ai", tags=["ai"])


class AskRequest(BaseModel):
    prompt: str


@router.post("/ask")
async def ask_ai(req: AskRequest):
    try:
        ai = AIClient()
        # "The Librarian" is the standard role for user interaction in this system
        # Run in threadpool to avoid blocking the event loop (and thus the health check)
        answer = await run_in_threadpool(ai.ask, Agents.LIBRARIAN, f"User request: {req.prompt}")
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
