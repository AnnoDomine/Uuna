SELECT table_name, column_name, discovery, confidence 
FROM research.discoveries 
WHERE discovery ILIKE ? OR table_name ILIKE ? 
ORDER BY confidence DESC 
LIMIT ?;
