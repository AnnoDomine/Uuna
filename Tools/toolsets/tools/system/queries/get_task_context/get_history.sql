SELECT 
    t.task_id, 
    t.query as original_query, 
    t.status as task_status,
    t.assigned_builds,
    e.event_id, 
    e.target_role, 
    e.output_data, 
    e.agent_confidence
FROM research.tasks t
LEFT JOIN research.task_events e ON t.task_id = e.task_id
WHERE t.task_id = ?
ORDER BY e.created_at ASC;
