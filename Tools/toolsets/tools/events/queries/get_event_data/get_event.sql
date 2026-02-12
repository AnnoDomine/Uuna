SELECT event_id, task_id, initiator_role, target_role, input_data, agent_confidence, max_potential
FROM research.task_events
WHERE event_id = ?;
