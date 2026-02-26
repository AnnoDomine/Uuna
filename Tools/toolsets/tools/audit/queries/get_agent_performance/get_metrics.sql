SELECT 
    initiator_role, 
    AVG(agent_confidence), 
    COUNT(*) 
FROM research.task_events 
WHERE initiator_role = ? 
GROUP BY initiator_role;
