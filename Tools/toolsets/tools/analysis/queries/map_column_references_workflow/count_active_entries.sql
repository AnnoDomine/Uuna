SELECT COUNT(*) FROM archive."{table_name}" WHERE "{column_name}" NOT IN (0, -1) AND "{column_name}" IS NOT NULL;
