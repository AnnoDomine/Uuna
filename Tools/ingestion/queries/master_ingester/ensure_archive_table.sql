CREATE TABLE IF NOT EXISTS archive."{table}" AS 
SELECT *, ''::VARCHAR as _row_hash FROM {temp_table} WHERE 1=0;