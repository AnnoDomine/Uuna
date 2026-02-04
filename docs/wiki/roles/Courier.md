# 🏃‍♂️ The Courier (The Torchbearer)
![Courier](../images/courier.svg)

[⬅️ Back to Home](../Home.md)

The Courier is the heart of the orchestration system. They manage the "Torch" (the Event ID) and ensure it reaches the next runner in the relay race.

## Responsibilities
*   **Strategic Routing**: Decides the path of information between specialists.
*   **Efficiency**: Aims for the shortest, safest route to verified knowledge.
*   **Tracking**: Maintains the `task_id` and logs every transition in the Chronicle.

## The Handover Logic
1.  **Commission**: Receives a `task_id` from the **Librarian** to begin orchestration.
2.  **Notification**: Receives a ping that an agent's Event is finished.
3.  **Analyze**: Look at the metadata of the finished Event (Outcome, Destination hints).
4.  **Handoff**: Trigger the next role by sending them the `Task ID` and the current `Event ID`.

## The "Not Ready" Feedback Loop
Agents have the right to refuse a task if the required context is missing.
*   **Rejection Message**: "This request is not yet ready for my processing."
*   **Courier Action**: When receiving this feedback, the Courier must analyze the `event_logs` to find missing dependencies and re-route accordingly.

## Evaluation Metric
The Courier is judged at the end of the request cycle by the **Tinker** and **Observer** based on the **Intelligence of the Path**. Unnecessary detours or skipping safety checks (Sentinel) will result in a lower Global Task-Score.
