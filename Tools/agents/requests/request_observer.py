from pathlib import Path

from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.agent_models import ObserverVerdict, ResearchLearning
from Tools.agents.requests.request_courier import present_response
from Tools.core.ai_schema_validator import request_with_schema
from Tools.core.shared_db_instance import db
from Tools.toolsets import global_tool_set
from Tools.toolsets.observer_tool_set import grant_final_verdict
from Tools.toolsets.tools.system.notify_frontend import notify_frontend

QUERY_DIR = Path("Tools/toolsets/tools/audit/queries/evaluate_agent_output")


def _load_query(name: str) -> str:
    """Loads a SQL query from the outsourced directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def request_observer(task_id: str):
    """
    Evaluates the quality of the research, assigns scores, and stores lessons in vector memory.
    """
    try:
        from Tools.core.api.managers.vector_manager import VectorManager

        vm = VectorManager()

        notify_frontend(
            task_id, "Observer: Mercilessly auditing research quality...", agent="Observer", type="research"
        )

        # 1. Get task context and history (including max_potential from Tinker)
        task_ctx = global_tool_set.get_task_context(task_id=task_id)
        if "error" in task_ctx:
            raise Exception(task_ctx["error"])

        history = task_ctx.get("history", [])
        if not history:
            notify_frontend(
                task_id, "Observer: No history to audit.", agent="Observer", type="research", level="warning"
            )
            return

        # 2. AI assessment of quality
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are the Observer. The Sages have already approved the content. Your job is to audit the quality of the execution. For each event, compare the output against the goal and the 'Max Potential' score. Be strict.",
                },
                {"role": "user", "content": f"TASK: {task_ctx['task']}\n\nHISTORY (with Potential Scores):\n{history}"},
            ]
        }

        verdict = request_with_schema(ObserverVerdict, payload, Agents.OBSERVER)

        if "error" in verdict:
            raise Exception(verdict["error"])

        # 3. Apply individual scores to ScoreBoard
        sql_save_score = _load_query("save_event_score")
        total_quality_points = 0
        total_max_potential = 0

        for eval_item in verdict["evaluations"]:
            # Find the corresponding event in history to get max_potential
            event_data = next((e for e in history if e["event_id"] == eval_item["event_id"]), None)
            if event_data and event_data.get("max_potential", 0) > 0:
                total_quality_points += eval_item["quality_score"]
                total_max_potential += event_data["max_potential"]

                percent = (eval_item["quality_score"] / event_data["max_potential"]) * 100
                percent = min(percent, 100.0)

                # Use the outsourced query
                db.execute(sql_save_score, [task_id, eval_item["event_id"], percent])

        # Calculate overall success
        overall_percent = (total_quality_points / total_max_potential * 100) if total_max_potential > 0 else 0

        # 4. Finalize Task Metadata
        grant_final_verdict(
            task_id=task_id,
            decision="APPROVE",  # Mark as complete in DB
            summary=verdict["overall_summary"],
        )

        # 5. Learning Phase: Extract and store lessons if quality is GOOD or better
        if overall_percent >= 60:
            notify_frontend(
                task_id,
                "Observer: Quality sufficient. Extracting lessons for long-term memory...",
                agent="Observer",
                type="research",
            )

            learning_payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are the Observer. Analyze the research task and extract high-value 'Lessons Learned' for each involved agent. Focus on facts, table relations, or successful research strategies.",
                    },
                    {
                        "role": "user",
                        "content": f"TASK: {task_ctx['task']}\n\nEVALUATIONS:\n{verdict.model_dump_json()}",
                    },
                ]
            }

            learnings = request_with_schema(ResearchLearning, learning_payload, Agents.OBSERVER)

            if "lessons" in learnings:
                for item in learnings["lessons"]:
                    vm.add_memory(
                        role=item["role"],
                        content=item["lesson"],
                        metadata={"task_id": task_id, "quality_score": item["quality_score"], "type": "lesson_learned"},
                    )
                notify_frontend(
                    task_id,
                    f"Observer: Successfully stored {len(learnings['lessons'])} lessons in long-term memory.",
                    agent="Observer",
                    type="research",
                )

        notify_frontend(
            task_id,
            f"Observer: Audit complete ({verdict['audit_status']}). Quality Score: {overall_percent:.1f}%",
            agent="Observer",
            type="research",
        )
        present_response(task_id)

    except Exception as e:
        notify_frontend(task_id, f"Observer scoring error: {e}", agent="Observer", type="error", level="error")
        return {"error": str(e)}
