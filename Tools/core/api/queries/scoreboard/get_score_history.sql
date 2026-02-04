SELECT s.*, e.target_role as role 
FROM research.score_board s
LEFT JOIN research.task_events e ON s.event_id = e.event_id
WHERE e.target_role = ? OR s.event_id IS NULL
ORDER BY s.created_at DESC;