SELECT id, table_name, column_name, data_type, min_val, max_val 
FROM research.column_features 
WHERE build_id = ? AND column_name NOT IN ('ID', 'build_id') 
LIMIT ?
