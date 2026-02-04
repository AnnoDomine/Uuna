-- Initialize Research Task & Scoring Infrastructure
CREATE SCHEMA IF NOT EXISTS research;

-- 1. Tasks Table
CREATE TABLE IF NOT EXISTS research.tasks (
    task_id UUID PRIMARY KEY,
    query TEXT,
    output TEXT,
    status VARCHAR,
    current_location VARCHAR,
    assigned_builds JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Task Events Table
CREATE TABLE IF NOT EXISTS research.task_events (
    event_id UUID PRIMARY KEY,
    task_id UUID,
    initiator_role VARCHAR,
    target_role VARCHAR,
    input_data JSON,
    output_data JSON,
    agent_confidence DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Event Logs Table
CREATE TABLE IF NOT EXISTS research.event_logs (
    log_id SEQUENCE PRIMARY KEY,
    event_id UUID,
    task_id UUID,
    role VARCHAR,
    log_entry TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Score Board Table
CREATE TABLE IF NOT EXISTS research.score_board (
    score_id SEQUENCE PRIMARY KEY,
    task_id UUID,
    event_id UUID,
    final_percent DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
