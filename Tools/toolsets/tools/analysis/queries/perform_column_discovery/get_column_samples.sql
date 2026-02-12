SELECT DISTINCT t."{col}" 
FROM archive.data_{table} t 
JOIN archive.build_data_map m ON t._row_hash = m.row_hash 
WHERE m.build_id = ? AND m.table_name = ? 
LIMIT 10
