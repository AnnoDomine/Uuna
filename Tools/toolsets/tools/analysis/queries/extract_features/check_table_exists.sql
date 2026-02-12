SELECT count(*) 
FROM information_schema.tables 
WHERE table_schema = 'archive' 
AND table_name = ?;