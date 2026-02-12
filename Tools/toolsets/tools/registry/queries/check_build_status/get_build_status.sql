SELECT version, is_downloaded, indexed 
FROM registry.builds 
WHERE version = ?;
