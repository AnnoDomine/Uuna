from flask import Flask, render_template_string, request, Response, stream_with_context
import sqlite3
import os
import glob
import json
import threading
import time
from sync_wow_db import fetch_and_import, fetch_available_builds

app = Flask(__name__)

# Global log storage for the UI
sync_logs = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>WoW Datamine Toolkit</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body { background: #121212; color: #e0e0e0; padding: 20px; }
        .table-container { overflow-x: auto; background: #1e1e1e; padding: 15px; border-radius: 8px; }
        table { color: #e0e0e0 !important; }
        .nav-link { color: #00bcd4; }
        .nav-link:hover { color: #fff; }
        .active-table { background: #333; font-weight: bold; }
        .sidebar { height: 90vh; overflow-y: auto; }
        .ref-link { color: #00bcd4; text-decoration: none; border-bottom: 1px dashed #00bcd4; }
        .ref-link:hover { color: #fff; border-bottom: 1px solid #fff; }
        .name-preview { color: #888; font-size: 0.85em; display: block; }
        #sync-log { background: #000; color: #0f0; font-family: monospace; padding: 10px; height: 300px; overflow-y: auto; border-radius: 5px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">WoW Datamine Toolkit</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Explorer</a>
                <a class="nav-link" href="/builds">Builds / Sync</a>
                <a class="nav-link" href="/compare">Compare</a>
            </div>
        </div>
    </nav>

    <div class="container-fluid">
        {% block content %}{% endblock %}
    </div>

    <script>
        if (document.getElementById('sync-log')) {
            const source = new EventSource("/sync-stream");
            source.onmessage = function(event) {
                const log = document.getElementById('sync-log');
                const line = document.createElement('div');
                line.textContent = event.data;
                log.appendChild(line);
                log.scrollTop = log.scrollHeight;
            };
        }
    </script>
</body>
</html>
"""

EXPLORER_TEMPLATE = """
{% extends "base" %}
{% block content %}
<div class="row mb-3">
    <div class="col-12 d-flex justify-content-between align-items-center">
        <form action="/" method="get" class="row g-3 align-items-center">
            <div class="col-auto">
                <label for="db_select" class="col-form-label">Database:</label>
            </div>
            <div class="col-auto">
                <select name="db" id="db_select" class="form-select bg-dark text-light" onchange="this.form.submit()">
                    {% for d in dbs %}
                        <option value="{{ d }}" {{ 'selected' if d == current_db }}>{{ d }}</option>
                    {% endfor %}
                </select>
            </div>
        </form>
        <div class="text-muted">
            Build: {{ current_db.split('_')[-1].replace('.db', '') }}
        </div>
    </div>
</div>
<div class="row">
    <nav class="col-md-2 d-none d-md-block sidebar border-end border-secondary">
        <h4>Tables</h4>
        <div class="list-group list-group-flush">
            {% for table in tables %}
                <a href="/?table={{ table }}&db={{ current_db }}" class="list-group-item list-group-item-action bg-dark text-light py-1 px-2 {{ 'active-table' if table == current_table }}">
                    {{ table }}
                </a>
            {% endfor %}
        </div>
    </nav>
    <main class="col-md-10 ms-sm-auto px-md-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h2>Table: {{ current_table }}</h2>
            <form action="/" method="get" class="d-flex">
                <input type="hidden" name="table" value="{{ current_table }}">
                <input type="hidden" name="db" value="{{ current_db }}">
                <input type="text" name="search" class="form-control bg-dark text-light me-2" placeholder="Search..." value="{{ search_val }}">
                <button class="btn btn-primary" type="submit">Search</button>
            </form>
        </div>
        <div class="table-container">
            <table class="table table-dark table-striped table-hover">
                <thead>
                    <tr>
                        {% for col in columns %} 
                            <th>
                                {{ col }}
                                {% if col in ref_map %}
                                    <span class="badge bg-info text-dark" style="font-size: 0.6em">REF: {{ ref_map[col] }}</span>
                                {% endif %}
                            </th> 
                        {% endfor %} 
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                        <tr>
                            {% for col in columns %}
                                <td>
                                    {% if col in ref_map and row[col] and row[col] not in (0, -1, '0', '-1') %}
                                        <a class="ref-link" href="/?db={{ current_db }}&table={{ ref_map[col] }}&search={{ row[col] }}">
                                            {{ row[col] }}
                                        </a>
                                        {% if row[col+'_name'] %}
                                            <span class="name-preview">{{ row[col+'_name'] }}</span>
                                        {% endif %}
                                    {% else %}
                                        {{ row[col] }}
                                    {% endif %}
                                </td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </main>
</div>
{% endblock %}
"""

BUILDS_TEMPLATE = """
... (same as before) ...
"""

COMPARE_TEMPLATE = """
{% extends "base" %}
{% block content %}
<div class="row">
    <div class="col-md-4">
        <h2>Compare Builds</h2>
        <form action="/compare" method="get" class="card bg-dark p-3">
            <div class="mb-3">
                <label class="form-label">Source Build (Old)</label>
                <select name="old" class="form-select bg-dark text-light">
                    {% for d in downloaded %}
                        <option value="{{ d }}" {{ 'selected' if d == old_ver }}>{{ d }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Target Build (New)</label>
                <select name="new" class="form-select bg-dark text-light">
                    {% for d in downloaded %}
                        <option value="{{ d }}" {{ 'selected' if d == new_ver }}>{{ d }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-check mb-3">
                <input class="form-check-input" type="checkbox" name="intermediate" id="intermediate" {{ 'checked' if intermediate }}>
                <label class="form-check-label" for="intermediate">
                    Show intermediate steps (if available)
                </label>
            </div>
            <button type="submit" class="btn btn-primary w-100">Compare</button>
        </form>
    </div>
    <div class="col-md-8">
        {% if results %}
            {% for res in results %}
                <div class="card bg-dark border-secondary mb-4">
                    <div class="card-header bg-secondary text-white">
                        <strong>{{ res.v1 }} &rarr; {{ res.v2 }}</strong>
                    </div>
                    <div class="card-body">
                        {% if res.diff.error %}
                            <div class="alert alert-danger">{{ res.diff.error }}</div>
                        {% else %}
                            <div class="row">
                                <div class="col-md-4">
                                    <h5 class="text-success">Added: {{ res.diff.added_tables|length }}</h5>
                                    <ul class="small">
                                        {% for t in res.diff.added_tables %}
                                            <li>{{ t.name }} ({{ t.count }})</li>
                                        {% endfor %}
                                    </ul>
                                </div>
                                <div class="col-md-4">
                                    <h5 class="text-danger">Removed: {{ res.diff.removed_tables|length }}</h5>
                                    <ul class="small">
                                        {% for t in res.diff.removed_tables %}
                                            <li>{{ t.name }} ({{ t.count }})</li>
                                        {% endfor %}
                                    </ul>
                                </div>
                                <div class="col-md-4">
                                    <h5 class="text-warning">Modified: {{ res.diff.modified_tables|length }}</h5>
                                    <ul class="small">
                                        {% for table, changes in res.diff.modified_tables.items() %}
                                            <li>
                                                <strong>{{ table }}</strong>
                                                <ul class="ps-2">
                                                    {% for c in changes %}<li>{{ c }}</li>{% endfor %}
                                                </ul>
                                            </li>
                                        {% endfor %}
                                    </ul>
                                </div>
                            </div>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="alert alert-info">Select builds to compare.</div>
        {% endif %}
    </div>
</div>
{% endblock %}
"""

def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_table_name_col(cursor, table):
    try:
        cursor.execute(f"PRAGMA table_info('{table}')")
        cols = [col[1] for col in cursor.fetchall()]
        for name in ['Name_lang', 'Text_lang', 'Title_lang', 'Name', 'Text', 'Title']:
            if name in cols: return name
    except: pass
    return None

@app.route("/")
def index():
    dbs = glob.glob('Data/dbs/WoW_Data_*.db')
    if not dbs: return "No databases found in Data/dbs/."
    current_db = request.args.get("db", dbs[0])
    
    ref_file = current_db.replace('.db', '_refs.json')
    all_refs = {}
    if os.path.exists(ref_file):
        with open(ref_file, 'r') as f: all_refs = json.load(f)
    
    conn = get_db_connection(current_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    
    current_table = request.args.get("table", tables[0] if tables else "")
    search_val = request.args.get("search", "")
    table_refs = {ref['column']: ref['target_table'] for ref in all_refs.get(current_table, [])}
    
    columns, rows = [], []
    if current_table:
        cursor.execute(f"PRAGMA table_info('{current_table}')")
        columns = [col[1] for col in cursor.fetchall()]
        query = f"SELECT * FROM '{current_table}'"
        params = []
        if search_val:
            where_clauses = [f'\"{col}\" = ?' for col in columns] + [f'\"{col}\" LIKE ?' for col in columns]
            query += " WHERE " + " OR ".join(where_clauses)
            params = [search_val] * len(columns) + [f"%{search_val}%"] * len(columns)
        
        query += " LIMIT 500"
        cursor.execute(query, params)
        for rr in cursor.fetchall():
            row_dict = dict(rr)
            for col, target in table_refs.items():
                val = row_dict.get(col)
                if val and val not in (0, -1, '0', '-1'):
                    name_col = get_table_name_col(cursor, target)
                    if name_col:
                        try:
                            cursor.execute(f"SELECT \"{name_col}\" FROM \"{target}\" WHERE ID = ?", (val,))
                            name_res = cursor.fetchone()
                            if name_res: row_dict[col+'_name'] = name_res[0]
                        except: pass
            rows.append(row_dict)
    conn.close()
    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', EXPLORER_TEMPLATE), dbs=dbs, current_db=current_db, tables=tables, current_table=current_table, columns=columns, rows=rows, search_val=search_val, ref_map=table_refs)

@app.route("/builds")
def builds():
    available = fetch_available_builds()
    downloaded = [os.path.basename(f).replace('WoW_Data_', '').replace('.db', '') for f in glob.glob('Data/dbs/WoW_Data_*.db')]
    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', BUILDS_TEMPLATE), available_builds=available, downloaded_builds=downloaded, logs=sync_logs)

@app.route("/compare")
def compare():
    downloaded = [os.path.basename(f).replace('WoW_Data_', '').replace('.db', '') for f in sorted(glob.glob('Data/dbs/WoW_Data_*.db'), reverse=True)]
    old_ver = request.args.get('old')
    new_ver = request.args.get('new')
    intermediate = request.args.get('intermediate') == 'on'
    
    results = []
    if old_ver and new_ver:
        from compare_builds import compare_builds, get_version_tuple
        from sync_wow_db import fetch_available_builds
        
        if not intermediate:
            res = compare_builds(old_ver, new_ver)
            results.append({"v1": old_ver, "v2": new_ver, "diff": res})
        else:
            available_online = fetch_available_builds()
            try:
                available_online.sort(key=get_version_tuple)
            except:
                available_online.sort()
            
            if old_ver in available_online and new_ver in available_online:
                idx_start = available_online.index(old_ver)
                idx_end = available_online.index(new_ver)
                if idx_start > idx_end: idx_start, idx_end = idx_end, idx_start
                
                build_range = available_online[idx_start:idx_end+1]
                for i in range(len(build_range) - 1):
                    v1, v2 = build_range[i], build_range[i+1]
                    # Only compare if both exist locally
                    if os.path.exists(f'Data/dbs/WoW_Data_{v1}.db') and os.path.exists(f'Data/dbs/WoW_Data_{v2}.db'):
                        res = compare_builds(v1, v2)
                        results.append({"v1": v1, "v2": v2, "diff": res})
                    else:
                        results.append({"v1": v1, "v2": v2, "diff": {"error": "Local database missing for one of these builds."}})

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', COMPARE_TEMPLATE), downloaded=downloaded, old_ver=old_ver, new_ver=new_ver, intermediate=intermediate, results=results)

@app.route("/sync", methods=['POST'])
def sync():
    build = request.form.get('build')
    table = request.form.get('table')
    tables = [table] if table else None
    
    def run_sync():
        sync_logs.clear()
        fetch_and_import(build, tables=tables, progress_callback=lambda msg: sync_logs.append(msg))
        # Remap references
        try:
            from map_references import map_references
            sync_logs.append("Updating reference map...")
            map_references(f'Data/dbs/WoW_Data_{build}.db')
            sync_logs.append("References updated.")
        except Exception as e:
            sync_logs.append(f"Error during reference mapping: {e}")

    threading.Thread(target=run_sync).start()
    return render_template_string("<script>window.location.href='/builds';</script>")

@app.route("/sync-stream")
def sync_stream():
    def event_stream():
        last_idx = 0
        while True:
            if last_idx < len(sync_logs):
                for i in range(last_idx, len(sync_logs)):
                    yield f"data: {sync_logs[i]}\n\n"
                last_idx = len(sync_logs)
            time.sleep(0.5)
    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
