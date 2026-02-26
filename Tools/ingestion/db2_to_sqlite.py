import sqlite3
import csv
import os
import glob


def create_db_from_csv(csv_dir, db_path):
    """Converts a folder full of CSV DB2 exports into a SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    print(f"Files found: {len(csv_files)}")

    for file_path in csv_files:
        table_name = os.path.basename(file_path).replace(".csv", "")
        print(f"Processing table: {table_name}...")

        with open(file_path, "r", encoding="utf-8") as f:
            # wow.export usually uses comma as a delimiter
            reader = csv.DictReader(f)
            columns = reader.fieldnames

            if not columns:
                continue

            # Clean column names and create table
            cols_str = ", ".join([f'"{c}"' for c in columns])
            cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
            cursor.execute(f'CREATE TABLE "{table_name}" ({cols_str})')

            # Insert data in batches for better performance
            placeholders = ", ".join(["?" for _ in columns])
            insert_query = f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({placeholders})'

            batch = []
            for row in reader:
                batch.append(tuple(row[c] for c in columns))
                if len(batch) >= 1000:
                    cursor.executemany(insert_query, batch)
                    batch = []

            if batch:
                cursor.executemany(insert_query, batch)

            conn.commit()

    conn.close()
    print("\nDone! Database created at: " + db_path)


if __name__ == "__main__":
    CSV_IMPORT_DIR = "Data/DB2_CSV"
    # Default to a generic path, but usually sync_wow_db is preferred
    SQLITE_DB_PATH = "Data/dbs/WoW_Data_Local.db"

    if not os.path.exists("Data/dbs"):
        os.makedirs("Data/dbs")

    if os.path.exists(CSV_IMPORT_DIR):
        create_db_from_csv(CSV_IMPORT_DIR, SQLITE_DB_PATH)
    else:
        if not os.path.exists(CSV_IMPORT_DIR):
            os.makedirs(CSV_IMPORT_DIR)
        print(f"Please place the CSV exports in the folder: {CSV_IMPORT_DIR}")
