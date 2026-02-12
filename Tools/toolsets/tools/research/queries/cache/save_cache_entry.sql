INSERT INTO research.online_cache (url, content, source_type, created_at)
VALUES (?, ?, ?, CURRENT_TIMESTAMP)
ON CONFLICT (url) DO UPDATE SET content = excluded.content, created_at = excluded.created_at
