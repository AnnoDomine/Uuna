SELECT created_at, role, log_entry 
FROM research.event_logs 
ORDER BY created_at DESC 
LIMIT ?;