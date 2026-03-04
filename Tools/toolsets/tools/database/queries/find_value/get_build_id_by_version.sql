SELECT id 
FROM registry.builds 
WHERE ? IN (version, id::VARCHAR);
