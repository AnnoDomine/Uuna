SELECT * FROM research.event_logs 
WHERE task_id = ? 
ORDER BY created_at ASC;