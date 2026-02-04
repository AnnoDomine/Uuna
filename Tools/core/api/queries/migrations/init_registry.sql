CREATE SCHEMA IF NOT EXISTS registry;
CREATE TABLE IF NOT EXISTS registry.migrations (
    migration_id SEQUENCE PRIMARY KEY,
    model_name VARCHAR,
    version INTEGER,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);