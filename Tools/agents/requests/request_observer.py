from typing import List
from pathlib import Path
from pydantic import BaseModel, Field
from Tools.agents.get_agent_skill_set import Agents
from Tools.toolsets import global_tool_set
from Tools.toolsets.observer_tool_set import grant_final_verdict
from Tools.core.ai_schema_validator import request_with_schema
from Tools.toolsets.tools.system.notify_frontend import notify_frontend
from Tools.core.shared_db_instance import db

QUERY_DIR = Path("Tools/toolsets/tools/audit/queries/evaluate_agent_output")


def _load_query(name: str) -> str:
    """Loads a SQL query from the outsourced directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


class EventEvaluation(BaseModel):
    event_id: str = Field(..., description="The UUID of the event.")
    quality_score: int = Field(..., description="The awarded quality points (0 to Max Potential).", ge=0)
    honesty_rating: str = Field(..., description="Rating of the agent's honesty regarding their confidence (e.g., 'Excellent', 'Fair', 'Poor').")
    feedback: str = Field(..., description="Qualitative feedback for the agent.")


class ObserverVerdict(BaseModel):
    evaluations: List[EventEvaluation] = Field(..., description="Detailed evaluation for each event in the task history.")
    final_decision: str = Field(..., description="Final verdict: 'APPROVE' or 'BLOCK'.")
    overall_summary: str = Field(..., description="A comprehensive summary of the research quality and findings.")


def request_observer(task_id: str):
    """
    Evaluates the quality of the research and assigns final scores.
    """
    try:
        notify_frontend(task_id, "Observer: Mercilessly judging research quality...", agent="Observer", type="research")
        
        # 1. Get task context and history (including max_potential from Tinker)
        task_ctx = global_tool_set.get_task_context(task_id=task_id)
        if "error" in task_ctx:
            raise Exception(task_ctx["error"])
            
        history = task_ctx.get("history", [])
        if not history:
            notify_frontend(task_id, "Observer: No history to evaluate.", agent="Observer", type="research", level="warning")
            return

        # 2. AI assessment of quality
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are the Observer. Evaluate the research results in the history. For each event, compare the output against the initiator's goal and the 'Max Potential' score. Be strict.",
                },
                {"role": "user", "content": f"TASK: {task_ctx['task']}\n\nHISTORY (with Potential Scores):\n{history}"},
            ]
        }

        verdict = request_with_schema(ObserverVerdict, payload, Agents.OBSERVER)
        
        if "error" in verdict:
            raise Exception(verdict["error"])

        # 3. Apply individual scores to ScoreBoard
        sql_save_score = _load_query("save_event_score")
        for eval_item in verdict["evaluations"]:
            # Find the corresponding event in history to get max_potential
            event_data = next((e for e in history if e["event_id"] == eval_item["event_id"]), None)
            if event_data and event_data.get("max_potential", 0) > 0:
                percent = (eval_item["quality_score"] / event_data["max_potential"]) * 100
                percent = min(percent, 100.0)
                
                # Use the outsourced query
                db.execute(sql_save_score, [task_id, eval_item["event_id"], percent])

        # 4. Grant Final Verdict
        grant_final_verdict(
            task_id=task_id,
            decision=verdict["final_decision"],
            summary=verdict["overall_summary"]
        )
        
        notify_frontend(
            task_id, 
            f"Observer: Quality assessment complete. Verdict: {verdict['final_decision']}. {verdict['overall_summary']}", 
            agent="Observer", 
            type="research"
        )

    except Exception as e:
        notify_frontend(task_id, f"Observer scoring error: {e}", agent="Observer", type="error", level="error")
        return {"error": str(e)}
