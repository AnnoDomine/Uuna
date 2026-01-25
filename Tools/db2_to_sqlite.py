import sqlite3
import csv
import os
import glob

def create_db_from_csv(csv_dir, db_path):
    """Konvertiert einen Ordner voller CSV-DB2-Exports in eine SQLite Datenbank."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    print(f"Gefundene Dateien: {len(csv_files)}")

    for file_path in csv_files:
        table_name = os.path.basename(file_path).replace(".csv", "")
        print(f"Verarbeite Tabelle: {table_name}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # wow.export nutzt normalerweise Komma als Trenner
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            
            if not columns:
                continue

            # Spaltennamen säubern und Tabelle erstellen
            cols_str = ", ".join([f'"{c}"' for c in columns])
            cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
            cursor.execute(f'CREATE TABLE "{table_name}" ({cols_str})')
            
            # Daten blockweise einfügen für bessere Performance
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
    print("\nFertig! Datenbank erstellt unter: " + db_path)

if __name__ == "__main__":
    CSV_IMPORT_DIR = "Data/DB2_CSV"
    SQLITE_DB_PATH = "Data/WoW_Data.db"
    
    if not os.path.exists("Data"):
        os.makedirs("Data")
    
    if os.path.exists(CSV_IMPORT_DIR):
        create_db_from_csv(CSV_IMPORT_DIR, SQLITE_DB_PATH)
    else:
        if not os.path.exists(CSV_IMPORT_DIR):
            os.makedirs(CSV_IMPORT_DIR)
        print(f"Bitte lege die CSV-Exports in den Ordner: {CSV_IMPORT_DIR}")
