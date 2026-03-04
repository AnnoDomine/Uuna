SELECT COUNT(*) 
FROM archive."{table_name}" d
JOIN archive.build_data_map m ON d._row_hash = m.row_hash
WHERE ({where_clause}) 
  AND m.build_id = ? 
  AND m.table_name = '{table_name}';
