SELECT proposed_target, decision, reasoning 
FROM research.attempts 
WHERE table_name=? AND column_name=? 
ORDER BY timestamp DESC LIMIT 1
