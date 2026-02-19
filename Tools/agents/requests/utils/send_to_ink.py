import httpx
from fastapi import FastAPI

from Tools.toolsets import global_tool_set

app = FastAPI()


@app.post("/send-to-ink")
async def send_to_ink(task_id, message):
    try:
        task = global_tool_set.get_task_context(task_id)

        payload = {"task_id": task_id, "message": message, "task": task}
    except Exception as e:
        payload = {"task_id": task_id, "message": str(e), "task": task}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:3800/update", json=payload)
            return response.json()
    except Exception as e:
        return {"error": str(e)}
