SELECT * FROM research.event_logs 
WHERE event_id = ? 
ORDER BY created_at ASC;