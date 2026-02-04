SELECT 
    COUNT(DISTINCT t."{col}") as distinct_count,
    COUNT(t."{col}") as non_null_count,
    MIN(TRY_CAST(t."{col}" AS VARCHAR)) as min_val,
    MAX(TRY_CAST(t."{col}" AS VARCHAR)) as max_val,
    FIRST(TYPEOF(t."{col}")) as d_type
FROM archive."{table}" t
JOIN archive.build_data_map m ON t._row_hash = m.row_hash
WHERE m.build_id = ? AND m.table_name = ?;