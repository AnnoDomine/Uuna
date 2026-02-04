SELECT source_table, column_pattern, target_table 
FROM research.global_knowledge 
WHERE last_verified_build = ?