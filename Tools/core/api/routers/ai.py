from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from Tools.agents.get_agent_skill_set import Agents
from Tools.core.ai_client import AIClient
from Tools.core.security_utils import sanitize_user_prompt

router = APIRouter(prefix="/ai", tags=["ai"])


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
