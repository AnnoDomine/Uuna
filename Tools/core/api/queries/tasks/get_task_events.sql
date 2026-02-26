SELECT event_id, initiator_role as role, target_role as event, input_data as details, created_at as timestamp FROM research.task_events WHERE task_id = ? ORDER BY created_at ASC
