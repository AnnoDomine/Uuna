SELECT 
    column_pattern, 
    source_table, 
    target_table as existing_target, 
    confidence as existing_confidence,
    ai_notes
FROM research.global_knowledge
WHERE column_pattern = ? AND source_table = ?;
