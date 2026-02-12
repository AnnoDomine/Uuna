-- This query is designed to be formatted in Python, 
-- but the IDs themselves should be passed as parameters.
SELECT COUNT(DISTINCT ID) FROM archive."{table}" WHERE ID IN ({placeholders})
