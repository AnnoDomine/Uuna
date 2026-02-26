CREATE TABLE {temp_table} AS 
SELECT * FROM read_csv_auto('{csv_path}', sep='{sep}', all_varchar=True, ignore_errors=True, null_padding=True, parallel=False);