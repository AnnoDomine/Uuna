#!/bin/bash
# start_master_ingester.sh
# Startet den Batch-Lauf für eine definierte Anzahl an Builds

PYTHON=".venv/bin/python3"
SCRIPT="Tools/ingestion/master_ingester.py"
LOG="Data/logs/master_ingester.log"
LIMIT=${1:-100}

# Kill existing
pkill -9 -f master_ingester.py
sleep 1

echo "--- New Master Ingestion Batch Started: $(date) (Limit: $LIMIT) ---" >> "$LOG"
nohup env MAX_BUILDS=$LIMIT $PYTHON -u "$SCRIPT" >> "$LOG" 2>&1 &

PID=$!
echo "Master Ingester gestartet mit PID: $PID (Limit: $LIMIT)"
