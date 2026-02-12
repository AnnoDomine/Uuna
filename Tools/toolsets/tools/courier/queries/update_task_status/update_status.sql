UPDATE research.tasks 
SET status = ?, current_location = ?, updated_at = CURRENT_TIMESTAMP
WHERE task_id = ?;
