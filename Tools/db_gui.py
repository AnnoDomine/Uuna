from flask import Flask, render_template_string, request
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "Data/WoW_Data.db"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>WoW DB2 Explorer</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body { background: #121212; color: #e0e0e0; padding: 20px; }
        .table-container { overflow-x: auto; background: #1e1e1e; padding: 15px; border-radius: 8px; }
        table { color: #e0e0e0 !important; }
        .nav-link { color: #00bcd4; }
        .nav-link:hover { color: #fff; }
        .active-table { background: #333; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 d-none d-md-block sidebar">
                <h4>Tabellen</h4>
                <div class="list-group list-group-flush">
                    {% for table in tables %}
                        <a href="/?table={{ table }}" class="list-group-item list-group-item-action bg-dark text-light {{ 'active-table' if table == current_table }}">
                            {{ table }}
                        </a>
                    {% endfor %}
                </div>
            </nav>
            <main class="col-md-10 ms-sm-auto px-md-4">
                <h2>Tabelle: {{ current_table }}</h2>
                <form action="/" method="get" class="mb-3">
                    <input type="hidden" name="table" value="{{ current_table }}">
                    <div class="input-group">
                        <input type="text" name="search" class="form-control bg-dark text-light" placeholder="In allen Spalten suchen..." value="{{ search_val }}">
                        <button class="btn btn-primary" type="submit">Suchen</button>
                    </div>
                </form>
                <div class="table-container">
                    <table class="table table-dark table-striped table-hover">
                        <thead>
                            <tr>{% for col in columns %} <th>{{ col }}</th> {% endfor %} </tr>
                        </thead>
                        <tbody>
                            {% for row in rows %}
                                <tr>{% for cell in row %} <td>{{ cell }}</td> {% endfor %} </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </main>
        </div>
    </div>
</body>
</html>
"""

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabellenliste
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    
    current_table = request.args.get("table", tables[0] if tables else "")
    search_val = request.args.get("search", "")
    
    columns = []
    rows = []
    
    if current_table:
        cursor.execute(f"PRAGMA table_info('{current_table}')")
        columns = [col[1] for col in cursor.fetchall()]
        
        query = f"SELECT * FROM '{current_table}'"
        params = []
        if search_val:
            where_clauses = [f'"{col}" LIKE ?' for col in columns]
            query += " WHERE " + " OR ".join(where_clauses)
            params = [f"%{search_val}%"] * len(columns)
        
        query += " LIMIT 500"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
    conn.close()
    return render_template_string(HTML_TEMPLATE, tables=tables, current_table=current_table, columns=columns, rows=rows, search_val=search_val)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
