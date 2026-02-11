INSERT INTO archive."{table}" 
SELECT *, {hash_expr} as _row_hash 
FROM {temp_table} 
WHERE {hash_expr} NOT IN (SELECT _row_hash FROM archive."{table}");