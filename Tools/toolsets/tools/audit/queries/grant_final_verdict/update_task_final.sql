UPDATE research.tasks 
SET status = ?, output = ?, updated_at = CURRENT_TIMESTAMP
WHERE task_id = ?;
