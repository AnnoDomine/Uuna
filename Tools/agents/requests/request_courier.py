from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.request_archivist import request_archivist
from Tools.agents.requests.request_librarian import send_librarian_response
from Tools.agents.requests.request_sages import Approval, request_sages
from Tools.agents.requests.request_tinker import request_tinker
from Tools.agents.requests.utils.get_valid_return_json import request_with_schema
from Tools.toolsets import global_tool_set


def present_response(task_id):
    """
    Sends the task id to the librarian to present the research to the user
    """
    send_librarian_response(task_id)


def request_courier_from_sages(task_id, approval: str, context: str):
    """
    Parse the approval from the sage and
    - If approved, send the task id to the tinker to start scoring and the librarian to present the research to the user
    - If revoked, create a new event and restart the research queue
    """
    if approval == Approval.APPROVED:
        present_response(task_id)
        request_tinker(task_id)
        # Scoring flow
        pass
    else:  # create event with the current output
        new_event = global_tool_set.create_task_event(
            task_id, Agents.SAGES, Agents.COURIER, {"sages_response": approval, "approval_context": context}
        )
        if "error" in new_event:
            raise Exception(new_event.get("error", "No error spezified while create event"))

        new_event_id = new_event.get("event_id", -1)
        if new_event_id is -1:
            raise Exception(
                f"Error while creating event for task id {task_id}. From: {Agents.SAGES} - to: {Agents.COURIER}"
            )

        request_courier(task_id, event_id=new_event_id)


def request_courier(task_id: int, event_id: int):
    """
    This function defines the hole flow how the courier is working.

    1. Get task and event
    3. Select spezialist for next event
    4. Create new event
    5. Send new event to selected specialist

    Args:
        task_id (int): The related task id
        event_id (int): The related event id
    """
    output = []

    # Get task and event
    try:
        task = global_tool_set.get_task_context(task_id=task_id)
        if "error" in task:
            raise Exception(task.get("error", "No error output"))

        # If we have more than 80 items in the task history (events) we don not want to research more (could be run into loop otherwise). So we force to send task id to sages
        task_history = task.get("history", [])
        if len(task_history) > 80:
            request_sages(task_id)
            return

        output.append(task.task)

        event = global_tool_set.get_event_data(event_id=event_id)
        if "error" in event:
            raise Exception(event.get("error", "No error output"))
        output.append(event)

        select_spezalist_payload = {
            "messages": [
                {
                    "role": "system",
                    "content": f"Based on the current progress of the task ({task.task}) and the events ({task.history}) you select the next specialist.",
                },
                {"role": "user", "content": f"NEWEST EVENT:\n{event}"},
                {
                    "role": "user",
                    "content": f"The name of the selected spezialist should be lowercased with underscore instead of spaces.\nARCHIVIST -> '{Agents.ARCHIVIST}'\nEXPEDITION GROUP -> '{Agents.EXPEDITION_GROUP}'\nCARTOGRAPHER -> '{Agents.CARTOGRAPHER}'\nSAGES -> '{Agents.SAGES}'",
                },
                {
                    "role": "user",
                    "context": "ARCHIVIST:\nThe archivist inspect the world of warcraft game related databases to get information (relations, data, values, differences, etc.).\n",
                },
                {
                    "role": "user",
                    "context": "EXPEDITION_GROUP:\nThe expedition group search online in searchmachines, wikis, documentations and world of warcraft related pages for information.\nIMPORTANT NOTE: The expedition group sends findings to sanities.\n",
                },
                {
                    "role": "user",
                    "context": "CARTOGRAPHER:\nThe cartographer creates a mermaid chart to visualise connections, relations or whatever you want to show.\n",
                },
                {
                    "role": "user",
                    "context": "SAGES:\nIf you mean the task is finished, the sages is the next and last spezialist. The sages validate the logic of the input and the output for the user.\n",
                },
            ]
        }

        select_spezialist_response = {"spezialist": "string"}

        selection = request_with_schema(select_spezialist_response, select_spezalist_payload, Agents.COURIER)
        if "error" in selection:
            raise Exception(selection.get("error", "No error output"))

        output.append(selection)

        # create event with the current output
        new_event = global_tool_set.create_task_event(task_id, Agents.COURIER, selection.spezialist, output)
        if "error" in new_event:
            raise Exception(new_event.get("error", "No error spezified while create event"))

        new_event_id = new_event.get("event_id", -1)
        if new_event_id is -1:
            raise Exception(
                f"Error while creating event for task id {task_id}. From: {Agents.COURIER} - to: {selection.spezialist}"
            )

        match selection.spezialist:
            case Agents.ARCHIVIST:
                request_archivist(task_id, new_event_id)
                return
            case Agents.EXPEDITION_GROUP:
                # request_expedition_group(task_id, new_event_id)
                return
            case Agents.CARTOGRAPHER:
                # request_cartographer(task_id, new_event_id)
                return
            case Agents.SAGES:
                request_sages(task_id)
                return

        # If we are here means there is no spezialis selected. In this case we force to stop the loop and send the task id to the sages
        request_sages(task_id)

    except Exception as e:
        return {"error": str(e)}
