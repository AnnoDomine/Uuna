import duckdb
import os

DB_PATH = 'Data/WoW_Master.duckdb'

def fix_schema():
    con = duckdb.connect(DB_PATH)
    try:
        # Check if max_potential exists
        res = con.execute("PRAGMA table_info('research.task_events')").fetchall()
        cols = [r[1] for r in res]
        if 'max_potential' not in cols:
            print("Adding max_potential column to research.task_events")
            con.execute("ALTER TABLE research.task_events ADD COLUMN max_potential INTEGER DEFAULT 0")
        
        # Ensure dummy event exists for the demo
        con.execute("CREATE TABLE IF NOT EXISTS research.tasks (task_id UUID PRIMARY KEY, query TEXT, status VARCHAR, assigned_builds JSON, current_location VARCHAR, created_at TIMESTAMP, updated_at TIMESTAMP)")
        con.execute("CREATE TABLE IF NOT EXISTS research.task_events (event_id UUID PRIMARY KEY, task_id UUID, initiator_role VARCHAR, target_role VARCHAR, input_data JSON, output_data JSON, agent_confidence DOUBLE, max_potential INTEGER, created_at TIMESTAMP, updated_at TIMESTAMP)")
        
        # Insert a dummy task and event if they don't exist
        task_id = '1c6f4282-eddb-4f10-8916-6c3e18ab25e7'
        event_id = 'dummy-event'
        
        con.execute("INSERT OR IGNORE INTO research.tasks (task_id, query, status) VALUES (?, ?, ?)", [task_id, 'Demo Query', 'active'])
        con.execute("INSERT OR IGNORE INTO research.task_events (event_id, task_id, initiator_role, target_role, input_data, max_potential) VALUES (?, ?, ?, ?, ?, ?)", 
                    [event_id, task_id, 'Courier', 'Archivist', '{}', 100])
        
        print("Schema fixed and dummy data inserted.")
    finally:
        con.close()

if __name__ == "__main__":
    fix_schema()
