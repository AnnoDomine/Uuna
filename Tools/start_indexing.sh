#!/bin/bash
# start_indexing.sh - Startet den Mass-Indexer entkoppelt im Hintergrund

# Pfade
PYTHON=".venv/bin/python3"
INDEXER="Tools/analysis/mass_indexer.py"
LOG="Data/logs/mass_indexing.log"

# Bereinigen
pkill -9 -f mass_indexer.py
pkill -9 -f feature_extractor.py
sleep 1

# Starten mit unbuffered output und vollständiger Entkopplung
echo "--- Indexing Session Started: $(date) ---" > "$LOG"
nohup $PYTHON -u "$INDEXER" >> "$LOG" 2>&1 &

# PID speichern und ausgeben
PID=$!
echo $PID > Data/logs/mass_indexing.pid
echo "Indexer gestartet mit PID: $PID"
echo "Log-Datei: $LOG"
