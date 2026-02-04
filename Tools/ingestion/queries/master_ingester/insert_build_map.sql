INSERT INTO archive.build_data_map (build_id, table_name, row_hash) 
SELECT {build_id}, '{table}', {hash_expr} FROM temp_load;