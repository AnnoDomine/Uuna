UPDATE registry.builds 
SET is_downloaded = TRUE 
WHERE id IN (SELECT DISTINCT build_id FROM archive.build_data_map);