SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN is_downloaded THEN 1 END) as downloaded,
    COUNT(CASE WHEN indexed THEN 1 END) as indexed
FROM registry.builds;