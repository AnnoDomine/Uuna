import sqlite3
import os
import glob
import json
import threading
import asyncio
from typing import Optional
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
from contextlib import asynccontextmanager

from sync_wow_db import fetch_and_import, get_setting
from update_build_registry import update_registry, fetch_versions
from project_init import init_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_all()
    if get_setting("sync_builds_list_on_startup", "1") == "1":
        print("Auto-updating build registry on startup...")
        try:
            data = fetch_versions()
            update_registry(data)
        except Exception as e:
            print(f"Failed to auto-update registry: {e}")
    yield


app = FastAPI(title="WoW Datamine Toolkit", lifespan=lifespan)
templates = Jinja2Templates(directory="Tools/templates")

# Global state for sync tracking
sync_logs = []
is_syncing = False
current_sync_build = None
sync_lock = threading.Lock()


def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_table_name_col(cursor, table):
    try:
        cursor.execute(f"PRAGMA table_info('{table}')")
        cols = [col[1] for col in cursor.fetchall()]
        for name in ["Name_lang", "Text_lang", "Title_lang", "Name", "Text", "Title"]:
            if name in cols:
                return name
    except:
        pass
    return None


def save_setting(key, value):
    try:
        conn = sqlite3.connect("Data/dbs/Settings.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, str(value)),
        )
        conn.commit()
        conn.close()
    except:
        pass


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Optional[str] = None, table: Optional[str] = None, search: Optional[str] = None):
    dbs = sorted(glob.glob("Data/dbs/WoW_Data_*.db"), reverse=True)
    ui_theme = get_setting("ui_theme", "dark")

    if not dbs:
        return templates.TemplateResponse(
            "base.html",
            {"request": request, "ui_theme": ui_theme, "content": "<h2>No databases found. Run a sync first!</h2>"},
        )

    current_db = db if db and os.path.exists(db) else dbs[0]
    ref_file = current_db.replace(".db", "_refs.json")
    all_refs = {}
    if os.path.exists(ref_file):
        with open(ref_file, "r") as f:
            all_refs = json.load(f)

    conn = get_db_connection(current_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall() if row[0] not in ("builds", "sqlite_sequence")]

    current_table = table if table in tables else (tables[0] if tables else "")
    search_val = search or ""
    table_refs = {ref["column"]: ref["target_table"] for ref in all_refs.get(current_table, [])}

    columns, rows = [], []
    if current_table:
        cursor.execute(f'PRAGMA table_info("{current_table}")')
        columns = [col[1] for col in cursor.fetchall()]
        query = f'SELECT * FROM "{current_table}"'
        params = []
        if search_val:
            clauses = [f'"{c}" LIKE ?' for c in columns]
            query += " WHERE " + " OR ".join(clauses)
            params = [f"%{search_val}%"] * len(columns)
        query += " LIMIT 500"

        try:
            cursor.execute(query, params)
            for rr in cursor.fetchall():
                row_dict = dict(rr)
                for col, target in table_refs.items():
                    val = row_dict.get(col)
                    if val and val not in (0, -1, "0", "-1"):
                        name_col = get_table_name_col(cursor, target)
                        if name_col:
                            try:
                                cursor.execute(f'SELECT "{name_col}" FROM "{target}" WHERE ID = ?', (val,))
                                name_res = cursor.fetchone()
                                if name_res:
                                    row_dict[col + "_name"] = name_res[0]
                            except:
                                pass
                rows.append(row_dict)
        except Exception as e:
            print(f"Query error: {e}")
    conn.close()

    context = {
        "request": request,
        "dbs": dbs,
        "current_db": current_db,
        "tables": tables,
        "current_table": current_table,
        "columns": columns,
        "rows": rows,
        "search_val": search_val,
        "ref_map": table_refs,
        "ui_theme": ui_theme,
    }

    if request.headers.get("HX-Request") and request.headers.get("HX-Target") == "table-data-container":
        return templates.TemplateResponse("explorer_table.html", context)

    return templates.TemplateResponse("explorer.html", context)


@app.get("/builds", response_class=HTMLResponse)
async def builds(request: Request):
    builds_info = []
    db_reg = "Data/dbs/Build_Registry.db"
    ui_theme = get_setting("ui_theme", "dark")
    if os.path.exists(db_reg):
        try:
            conn = sqlite3.connect(db_reg)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT version, is_downloaded, last_synced FROM builds WHERE product='wow' ORDER BY id DESC LIMIT 50"
            )
            builds_info = [dict(row) for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            print(f"Registry error: {e}")

    return templates.TemplateResponse(
        "builds.html",
        {
            "request": request,
            "available_builds": builds_info,
            "logs": sync_logs,
            "ui_theme": ui_theme,
            "is_syncing": is_syncing,
            "current_sync_build": current_sync_build,
        },
    )


@app.get("/compare", response_class=HTMLResponse)
async def compare(request: Request, old: Optional[str] = None, new: Optional[str] = None):
    downloaded = [
        os.path.basename(f).replace("WoW_Data_", "").replace(".db", "")
        for f in sorted(glob.glob("Data/dbs/WoW_Data_*.db"), reverse=True)
    ]
    ui_theme = get_setting("ui_theme", "dark")
    results = []
    if old and new:
        from compare_builds import compare_builds

        res = compare_builds(old, new)
        results.append({"v1": old, "v2": new, "diff": res})

    context = {
        "request": request,
        "downloaded": downloaded,
        "old_ver": old,
        "new_ver": new,
        "results": results,
        "ui_theme": ui_theme,
    }
    if request.headers.get("HX-Request") and request.headers.get("HX-Target") == "results-area":
        return templates.TemplateResponse("compare_results.html", context)
    return templates.TemplateResponse("compare.html", context)


@app.post("/sync")
async def sync(request: Request, build: str = Form(...)):
    global is_syncing, current_sync_build

    if is_syncing:
        return HTMLResponse(
            content=f'<div class="alert alert-warning">Sync already in progress for {current_sync_build}</div>',
            status_code=409,
        )

    def run_sync():
        global is_syncing, current_sync_build
        with sync_lock:
            is_syncing = True
            current_sync_build = build
            sync_logs.clear()
            sync_logs.append(f"Starting sync for build {build}...")
            try:
                fetch_and_import(build, progress_callback=lambda msg: sync_logs.append(msg))
                from map_references import map_references

                sync_logs.append("Updating references...")
                map_references(f"Data/dbs/WoW_Data_{build}.db")
                sync_logs.append(f"Sync for build {build} completed.")
            except Exception as e:
                sync_logs.append(f"Error: {e}")
            finally:
                is_syncing = False
                current_sync_build = None

    threading.Thread(target=run_sync).start()
    return HTMLResponse(content='<div id="sync-log">Initializing sync session...</div>')


@app.get("/sync-stream")
async def sync_stream(request: Request):
    async def event_generator():
        last_idx = 0
        while True:
            if await request.is_disconnected():
                break
            if last_idx < len(sync_logs):
                for i in range(last_idx, len(sync_logs)):
                    yield f"data: {sync_logs[i]}\n\n"
                last_idx = len(sync_logs)
            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())


@app.get("/settings", response_class=HTMLResponse)
async def settings_get(request: Request):
    conn = sqlite3.connect("Data/dbs/Settings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM settings ORDER BY setting_group, name")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    grouped = {}
    for row in rows:
        grouped.setdefault(row["setting_group"], []).append(row)
    ui_theme = get_setting("ui_theme", "dark")
    return templates.TemplateResponse(
        "settings.html", {"request": request, "grouped_settings": grouped, "ui_theme": ui_theme}
    )


@app.post("/settings")
async def settings_post(request: Request):
    form_data = await request.form()
    conn = sqlite3.connect("Data/dbs/Settings.db")
    cursor = conn.cursor()
    cursor.execute("SELECT key, type FROM settings")
    db_settings = cursor.fetchall()
    for key, s_type in db_settings:
        new_val = ("1" if form_data.get(key) else "0") if s_type == "bool" else form_data.get(key)
        if new_val is not None:
            cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (str(new_val), key))
    conn.commit()
    conn.close()
    return HTMLResponse(content='<div class="alert alert-success">Settings updated successfully!</div>')


@app.post("/settings/toggle-theme")
def toggle_theme():
    current = get_setting("ui_theme", "dark")
    new_theme = "light" if current == "dark" else "dark"
    save_setting("ui_theme", new_theme)
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
