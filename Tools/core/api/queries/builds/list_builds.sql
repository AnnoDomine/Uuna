SELECT
    version,
    is_downloaded,
    indexed
FROM
    registry.builds
ORDER BY
    id ASC
