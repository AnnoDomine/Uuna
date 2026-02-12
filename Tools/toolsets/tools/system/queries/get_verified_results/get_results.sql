SELECT 
    initiator_role, 
    target_role, 
    output_data, 
    agent_confidence
FROM research.task_events
WHERE task_id = ? AND output_data IS NOT NULL
ORDER BY created_at ASC;
