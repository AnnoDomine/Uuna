SELECT DISTINCT t."{col}" 
FROM archive."{table}" t 
JOIN archive.build_data_map m ON t._row_hash = m.row_hash 
WHERE m.build_id = ? AND m.table_name = ? 
AND t."{col}" IS NOT NULL
LIMIT 10;