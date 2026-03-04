SELECT table_name 
FROM information_schema.columns 
WHERE table_schema = 'archive' 
  AND column_name = '_row_hash'
  AND table_name NOT LIKE 'tmp_%';
