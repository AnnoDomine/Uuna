#!/bin/bash
echo "--- Start sync and mapping for all known builds ---"

# 1. Update Registry
echo "--- Updating Build Registry ---"
.venv/bin/python3 Tools/update_build_registry.py

# 2. Get Build List (only not synced)
builds=$()
count=$(echo "$builds" | wc -l)

echo "--- Found $count builds. Starting Phase 1: Sync ---"

# Phase 1: Download/Sync
for build in $builds; do
    echo "-----------------------------------"
    echo "---- [SYNC] ---------- $build -----"
    .venv/bin/python3 Tools/sync_wow_db.py "$build"
    echo "---- Sync complete for $build -----"
    echo "-----------------------------------"
done

echo "--- Phase 1 complete. Starting Phase 2: Mapping ---"

# Phase 2: Analysis
for build in $builds; do
    echo "-----------------------------------"
    echo "--- [MAP] -------------- $build ---"
    .venv/bin/python3 Tools/map_references.py "$build" --headless
    echo "--- Mapping complete for $build ---"
    echo "-----------------------------------"
done

echo "--- All $count builds processed! ---"
