SELECT discovery FROM research.discoveries 
WHERE table_name=? AND column_name=? AND build_id != ? 
LIMIT 3
