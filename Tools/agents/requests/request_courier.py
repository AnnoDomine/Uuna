from pydantic import BaseModel, Field
from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.request_archivist import request_archivist
from Tools.agents.requests.request_librarian import send_librarian_response
from Tools.agents.requests.request_sages import ApprovalStatus, request_sages
from Tools.agents.requests.request_tinker import request_tinker
from Tools.core.ai_schema_validator import request_with_schema
from Tools.toolsets import global_tool_set
from Tools.toolsets.tools.system.notify_frontend import notify_frontend


class SpecialistSelection(BaseModel):
    specialist: Agents = Field(..., description="The name of the next specialist to handle the task.")


def present_response(task_id):
    """Sends the task id to the librarian to present the research to the user."""
    send_librarian_response(task_id)


def request_courier_from_sages(task_id, approval: str, context: str):
    """
    Parse the approval from the sage and
    - If approved, send the task id to the tinker to start scoring and the librarian to present the research to the user
    - If revoked, create a new event and restart the research queue
    """
    if approval == ApprovalStatus.APPROVED:
        notify_frontend(task_id, "Courier: Task approved by Sages. Finalizing...", agent="Courier", type="research")
        present_response(task_id)
        request_tinker(task_id)
    else:
        notify_frontend(task_id, f"Courier: Sages revoked approval ({approval}). Re-routing...", agent="Courier", type="research")
        new_event = global_tool_set.create_task_event(
            task_id, Agents.SAGES.value, Agents.COURIER.value, {"sages_response": approval, "approval_context": context}
        )
        if "error" in new_event:
            raise Exception("Failed to create follow-up event.")

        request_courier(task_id, event_id=new_event["event_id"])


def request_courier(task_id: str, event_id: str):
    """
    Handles task routing and specialist selection.
    """
    notify_frontend(task_id, "Courier: Analyzing task chain for next routing decision...", agent="Courier", type="research")
    output = []

    try:
        task_ctx = global_tool_set.get_task_context(task_id=task_id)
        if "error" in task_ctx:
            raise Exception(task_ctx["error"])

        task_history = task_ctx.get("history", [])
        if len(task_history) > 80:
            notify_frontend(task_id, "Courier: History limit reached. Forcing Sages verification.", agent="Courier", type="research", level="warning")
            request_sages(task_id)
            return

        output.append(task_ctx["task"])

        event = global_tool_set.get_event_data(event_id=event_id)
        if "error" in event:
            raise Exception(event["error"])
        output.append(event)

        select_payload = {
            "messages": [
                {
                    "role": "system",
                    "content": f"Based on the current progress of the task ({task_ctx['task']}) and the events ({task_history}), select the next specialist.",
                },
                {"role": "user", "content": f"NEWEST EVENT:\n{event}"},
                {
                    "role": "user",
                    "content": f"The name of the selected specialist should be one of: '{Agents.ARCHIVIST.value}', '{Agents.EXPEDITION_GROUP.value}', '{Agents.CARTOGRAPHER.value}', '{Agents.SAGES.value}'",
                },
            ]
        }

        selection = request_with_schema(SpecialistSelection, select_payload, Agents.COURIER)
        
        if "error" in selection:
            raise Exception(selection["error"])

        specialist = selection["specialist"]
        notify_frontend(task_id, f"Courier: Routing task to specialist '{specialist}'", agent="Courier", type="research")

        new_event = global_tool_set.create_task_event(task_id, Agents.COURIER.value, specialist, output)
        if "error" in new_event:
            raise Exception("Failed to create routing event.")

        match specialist:
            case Agents.ARCHIVIST.value:
                request_archivist(task_id, new_event["event_id"])
                return
            case Agents.SAGES.value:
                request_sages(task_id)
                return
            # Add other cases as implemented...

        # Fallback to Sages if no valid specialist was chosen
        request_sages(task_id)

    except Exception as e:
        notify_frontend(task_id, f"Courier routing error: {e}", agent="Courier", type="error", level="error")
        return {"error": str(e)}
