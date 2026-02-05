CREATE SCHEMA IF NOT EXISTS registry;
CREATE SEQUENCE IF NOT EXISTS registry.migration_seq;
CREATE TABLE IF NOT EXISTS registry.migrations (
    migration_id INTEGER PRIMARY KEY DEFAULT nextval('registry.migration_seq'),
    model_name VARCHAR,
    version INTEGER,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);