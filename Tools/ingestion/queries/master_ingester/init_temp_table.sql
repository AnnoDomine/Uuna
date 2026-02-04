CREATE TEMPORARY TABLE temp_load AS 
SELECT * FROM read_csv_auto('{csv_path}', sep='{sep}', all_varchar=True);