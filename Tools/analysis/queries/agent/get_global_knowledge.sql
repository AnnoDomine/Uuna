SELECT target_table, ai_notes 
FROM research.global_knowledge 
WHERE column_pattern=? AND source_table=?
