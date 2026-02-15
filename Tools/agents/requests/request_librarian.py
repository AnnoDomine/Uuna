from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests import request_courier
from Tools.agents.requests.utils.get_valid_return_json import request_with_schema
from Tools.toolsets import global_tool_set


def send_librarian_response(task_id):
    try:
        task = global_tool_set.get_task_context(task_id)

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Combine all information together and serve the summerised result to the user.",
                },
                {"role": "system", "context": task},
            ]
        }

        response = {"summary": "string"}

        final_summary = request_with_schema(response, payload, Agents.LIBRARIAN)

        # Add the final_summary to the task and set the task as finished
        print(final_summary)

    except Exception as e:
        return {"error": str(e)}


def request_librarian(promps, builds):
    """
    This function is the entry point to the research.
    It is called, when the request is sent from the user.

    1. Decide if the knowledge fits for the request (via confidence score)
    2. If the librarian decide there is no knowledge or confidence score is below 80%, we start the research
    3. If no research needed, present the result to the user
    4. If research is needed, start research process beginns with the courier after creating a task and an initial event (Add knowledge if provided)
    """
    output = []
    output.append({"user_promps": promps})
    output.append({"builds": builds})

    try:
        check_knowledge_payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Search to your knowledge and return it with a confidence score 0-100 based how good the knowledge fits to resolve the request directly. If you have no knowledge, the confidence is 100 and the knowledge is 'None'",
                },
                {"role": "user", "content": f"BUILD:{','.join(builds)}\nPROMPT:\n{promps}"},
            ]
        }

        check_knowledge_response = {"knowledge": "string", "confidence": 2}

        researched_knowledge = request_with_schema(check_knowledge_response, check_knowledge_payload, Agents.LIBRARIAN)
        if "error" in researched_knowledge:
            raise Exception(researched_knowledge.get("error", "No defined error"))

        knowledge, confidence = researched_knowledge["knowledge"], researched_knowledge["confidence"]
        output.append({"knowledge_context": knowledge, "knowledge_confidence": confidence})

        # create task with the current output
        new_task = global_tool_set.create_research_task(output, assigned_builds=builds)
        if "error" in new_task:
            raise Exception(new_task.get("error", "No error spezified while creating task"))

        new_task_id = new_task.get("task_id", -1)
        if new_task_id is -1:
            raise Exception("Error while creating task.")

        output.append(new_task)

        if knowledge == "None" or confidence < 80:
            # create event with the current output
            new_event = global_tool_set.create_task_event(new_task_id, Agents.LIBRARIAN, Agents.COURIER, output)
            if "error" in new_event:
                raise Exception(new_event.get("error", "No error spezified while create event"))

            new_event_id = new_event.get("event_id", -1)
            if new_event_id is -1:
                raise Exception(
                    f"Error while creating event for task id {new_task_id}. From: {Agents.LIBRARIAN} - to: {Agents.COURIER}"
                )

            # Start research
            request_courier(new_task_id, new_event_id)
        else:
            # Finalise task
            send_librarian_response(new_task_id)

    except Exception as e:
        return {"error": str(e)}
