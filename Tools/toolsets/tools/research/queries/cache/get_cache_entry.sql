SELECT content FROM research.online_cache 
WHERE url = ? AND created_at > (CURRENT_TIMESTAMP - (? * INTERVAL '1 hour'))
