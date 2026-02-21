from pydantic import BaseModel, Field
from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests import request_courier
from Tools.core.ai_schema_validator import request_with_schema
from Tools.toolsets import global_tool_set
from Tools.toolsets.tools.system.notify_frontend import notify_frontend
from Tools.core.security_utils import sanitize_user_prompt


class LibrarianSummary(BaseModel):
    summary: str = Field(..., description="The comprehensive summary of all researched information.")


class LibrarianResponse(BaseModel):
    knowledge: str = Field(..., description="The summarized knowledge found in the internal base, or 'None' if nothing relevant exists.")
    confidence: int = Field(..., description="Confidence score from 0 to 100 regarding the quality of the information.", ge=0, le=100)
    needs_more_research: bool = Field(..., description="True if the internal knowledge is insufficient and a deep archive search is required.")


def send_librarian_response(task_id):
    """Summarizes all task information and notifies the frontend."""
    try:
        notify_frontend(task_id, "Librarian: Finalizing research results...", agent="Librarian", type="research")
        
        task = global_tool_set.get_task_context(task_id)

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Combine all information together and serve the summarised result to the user.",
                },
                {"role": "system", "content": f"TASK CONTEXT:\n{task}"},
            ]
        }

        final_summary = request_with_schema(LibrarianSummary, payload, Agents.LIBRARIAN)

        if "summary" in final_summary:
            notify_frontend(task_id, final_summary["summary"], agent="Librarian", type="response")
        else:
            raise Exception("Failed to generate summary.")

    except Exception as e:
        notify_frontend(task_id, f"Error in finalization: {e}", agent="Librarian", type="error", level="error")
        return {"error": str(e)}


def request_librarian(prompts, builds):
    """
    Entry point for user requests. Handles initial knowledge check and task spawning.
    """
    output = [{"user_prompts": prompts}, {"builds": builds}]

    try:
        # Sanitize user prompts to prevent injection
        safe_prompts = sanitize_user_prompt(prompts)

        check_payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Search your knowledge and return it with a confidence score (0-100). If you have no knowledge, confidence is 100 and knowledge is 'None'.",
                },
                {"role": "user", "content": f"BUILD:{','.join(builds)}\nPROMPT:\n{safe_prompts}"},
            ]
        }

        researched = request_with_schema(LibrarianResponse, check_payload, Agents.LIBRARIAN)
        
        if "error" in researched:
            raise Exception(researched.get("error", "AI request failed"))

        knowledge = researched["knowledge"]
        confidence = researched["confidence"]
        needs_research = researched["needs_more_research"]

        output.append({
            "knowledge_context": knowledge, 
            "knowledge_confidence": confidence,
            "ai_decided_research": needs_research
        })

        # Create the central task
        new_task = global_tool_set.create_research_task(output, assigned_builds=builds)
        if "error" in new_task:
            raise Exception("Failed to create research task.")

        task_id = new_task["task_id"]
        notify_frontend(task_id, "Librarian: Request received. Analyzing knowledge base...", agent="Librarian", type="research")

        if needs_research:
            # Need deeper research via courier
            notify_frontend(task_id, "Librarian: Knowledge insufficient. Spawning research chain...", agent="Librarian", type="research")
            
            new_event = global_tool_set.create_task_event(task_id, Agents.LIBRARIAN.value, Agents.COURIER.value, output)
            if "error" in new_event:
                raise Exception("Failed to create initial event.")

            request_courier.request_courier(task_id, new_event["event_id"])
        else:
            # Knowledge is enough, finalize immediately
            send_librarian_response(task_id)

    except Exception as e:
        # We don't have a task_id yet if creation failed, but we should log it
        print(f"CRITICAL ERROR: {e}")
        return {"error": str(e)}
