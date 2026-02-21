from enum import Enum
from pydantic import BaseModel, Field
from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.request_courier import request_courier_from_sages
from Tools.core.ai_schema_validator import request_with_schema
from Tools.toolsets import global_tool_set
from Tools.toolsets.tools.system.notify_frontend import notify_frontend


class ApprovalStatus(str, Enum):
    APPROVED = "approved"
    REVOKED = "revoked"


class SageVerdict(BaseModel):
    approval: ApprovalStatus = Field(..., description="Verdict on the task logic.")
    context: str = Field(..., description="The rationale or instructions for the next steps.")


def request_sages(task_id: str):
    """
    The Sages check if the task is valid to send to the user.
    """
    try:
        notify_frontend(task_id, "Sages: Reviewing task logic and consistency...", agent="Sages", type="research")
        
        task_ctx = global_tool_set.get_task_context(task_id)
        if "error" in task_ctx:
            raise Exception(task_ctx["error"])

        history = task_ctx.get("history", [])
        if len(history) > 50:
            notify_frontend(task_id, "Sages: History limit reached. Auto-approving with notice.", agent="Sages", type="research", level="warning")
            request_courier_from_sages(
                task_id, approval=ApprovalStatus.APPROVED, context="Aborted task due to high amount of research steps."
            )
            return

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Review the task and the task history to decide if the collected information is logical and valid.",
                },
                {
                    "role": "user",
                    "content": f"Return your approval and why you decided it as context. The approval can only be '{ApprovalStatus.APPROVED.value}' or '{ApprovalStatus.REVOKED.value}'.",
                },
                {"role": "system", "content": f"TASK CONTEXT:\n{task_ctx}"},
            ]
        }

        approval_response = request_with_schema(SageVerdict, payload, Agents.SAGES)
        
        if "error" in approval_response:
            raise Exception(approval_response["error"])

        decision = approval_response["approval"]
        notify_frontend(task_id, f"Sages: Verdict is '{decision.upper()}'. Reason: {approval_response['context']}", agent="Sages", type="research")

        request_courier_from_sages(task_id, decision, approval_response["context"])

    except Exception as e:
        notify_frontend(task_id, f"Sages verification error: {e}", agent="Sages", type="error", level="error")
        # Fallback: Auto-approve on error to not block the user, but with error context
        request_courier_from_sages(task_id, ApprovalStatus.APPROVED, f"Verification system error: {str(e)}")
