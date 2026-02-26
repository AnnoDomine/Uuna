import duckdb
import os

DB_PATH = "Data/WoW_Master.duckdb"

try:
    print(f"Opening DB at {os.path.abspath(DB_PATH)}")
    with duckdb.connect(DB_PATH) as con:
        # Check if table exists
        tables = con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='research'"
        ).fetchall()
        print(f"Tables in research schema: {tables}")

        if ("tasks",) in tables:
            count = con.execute("SELECT count(*) FROM research.tasks").fetchone()[0]
            print(f"Row count in research.tasks: {count}")
            if count > 0:
                rows = con.execute("SELECT * FROM research.tasks LIMIT 5").fetchall()
                print(f"Sample rows: {rows}")
        else:
            print("Table research.tasks DOES NOT EXIST.")

except Exception as e:
    print(f"Error: {e}")
