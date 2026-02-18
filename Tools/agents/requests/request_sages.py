from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.request_courier import request_courier_from_sages
from Tools.agents.requests.utils.get_valid_return_json import request_with_schema
from Tools.toolsets import global_tool_set


class Approval:
    APPROVED = "approved"
    REVOKED = "revoked"


def request_sages(task_id):
    """
    The sages checks if the task is valid to send to the user.

    1. Check the validity of the tesk flow and the information which would be present to the user
    2. approve od revoke the task and sent the approval to the courier

    Additional: If we have more than 50 events in a task, the task will be automatic approved with the information
    'Task due high amount of research steps aborded.'

    Additional: If an error os raised, we approve the task with the related error message as context
    """
    try:
        task = global_tool_set.get_task_context(task_id)
        if "error" in task:
            raise Exception(task.get("error", f"No error spezified while getting task id: {task_id}"))

        history = task.get("history", [])
        if len(history) > 50:
            request_courier_from_sages(
                task_id, approval=Approval.APPROVED, context="Aborded task due the amount of research events."
            )

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Review the task and the task history to decide if the collected information are logic and valid.",
                },
                {
                    "role": "user",
                    "content": f"Return your approval and why you decided it as context. The approval can only have '{Approval.APPROVED}' or '{Approval.REVOKED}'.",
                },
            ]
        }

        response = {"approval": Approval, "context": "string"}

        approval_response = request_with_schema(response, payload, Agents.SAGES)
        if "error" in approval_response:
            raise Exception(approval_response.get("error", "No spezified error while approve task"))

        request_courier_from_sages(task_id, **approval_response)

    except Exception as e:
        error_response = {
            "approval": Approval.APPROVED,
            "context": str(e),
        }
        request_courier_from_sages(task_id, **error_response)
