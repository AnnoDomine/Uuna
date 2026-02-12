CREATE SCHEMA IF NOT EXISTS research;
CREATE SEQUENCE IF NOT EXISTS research.feature_id_seq;
CREATE TABLE IF NOT EXISTS research.features (
    id INTEGER PRIMARY KEY DEFAULT nextval('research.feature_id_seq'),
    build_id INTEGER,
    table_name VARCHAR,
    column_name VARCHAR,
    distinct_count INTEGER,
    min_val VARCHAR,
    max_val VARCHAR,
    data_type VARCHAR,
    samples JSON
);
CREATE SEQUENCE IF NOT EXISTS research.indexing_error_id_seq;
CREATE TABLE IF NOT EXISTS research.indexing_errors (
    id INTEGER PRIMARY KEY DEFAULT nextval('research.indexing_error_id_seq'),
    build_id INTEGER,
    table_name VARCHAR,
    error_type VARCHAR,
    message VARCHAR,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);