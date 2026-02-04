UPDATE research.task_events 
SET output_data = ?, agent_confidence = ?, updated_at = CURRENT_TIMESTAMP 
WHERE event_id = ?;