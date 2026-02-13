from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..managers.vector_manager import VectorManager

router = APIRouter(prefix="/memory", tags=["memory"])
vm = VectorManager()


class MemoryAddRequest(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = {}


class MemorySearchRequest(BaseModel):
    role: str
    query: str
    limit: Optional[int] = 5


@router.post("/add")
async def add_memory(req: MemoryAddRequest):
    mem_id = vm.add_memory(req.role, req.content, req.metadata)
    if not mem_id:
        raise HTTPException(status_code=500, detail="Failed to store memory")
    return {"status": "success", "id": mem_id}


@router.post("/search")
async def search_memory(req: MemorySearchRequest):
    results = vm.search_memory(req.role, req.query, req.limit)
    return {"results": results}
