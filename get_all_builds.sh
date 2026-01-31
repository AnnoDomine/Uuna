#!/bin/bash
echo "--- Start sync and mapping for all known builds ---"

# 1. Update Registry
echo "--- Updating Build Registry ---"
.venv/bin/python3 Tools/update_build_registry.py

# 2. Get Build List
builds=$(.venv/bin/python3 -c "import sqlite3; conn = sqlite3.connect('Data/dbs/Build_Registry.db'); cur = conn.cursor(); cur.execute('SELECT version FROM builds ORDER BY id ASC'); [print(r[0]) for r in cur.fetchall()]")
count=$(echo "$builds" | wc -l)

echo "--- Found $count builds. Starting Phase 1: Sync ---"

# Phase 1: Downloads
for build in $builds; do
    echo "[SYNC] --- $build ---"
    .venv/bin/python3 Tools/sync_wow_db.py "$build"
done

echo "--- Phase 1 complete. Starting Phase 2: Mapping ---"

# Phase 2: Analysis
for build in $builds; do
    echo "[MAP]  --- $build ---"
    .venv/bin/python3 Tools/map_references.py "$build" --headless
done

echo "--- All $count builds processed! ---"
