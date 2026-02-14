#!/bin/bash
# start_master_ingester.sh
# Startet den Batch-Lauf robust im Hintergrund

PYTHON="uv run python"
SCRIPT="Tools/ingestion/master_ingester.py"
LOG="Data/logs/master_ingester.log"
LIMIT=${1:-100}
WORKERS=${2:-4}

mkdir -p Data/logs
pkill -9 -f master_ingester.py
sleep 1

echo "--- Master Ingestion Batch Robust Start: $(date) (Limit: $LIMIT, Workers: $WORKERS) ---" >> "$LOG"

# Wir übergeben MAX_BUILDS, MAX_WORKERS und PYTHONPATH via env im Popen call
$PYTHON -c "import subprocess, os; env = os.environ.copy(); env['MAX_BUILDS'] = '$LIMIT'; env['MAX_WORKERS'] = '$WORKERS'; env['PYTHONPATH'] = os.getcwd(); subprocess.Popen(['python', '-u', '$SCRIPT'], stdout=open('$LOG', 'a'), stderr=subprocess.STDOUT, start_new_session=True, env=env)"

echo "Master Ingester gestartet (Limit: $LIMIT, Workers: $WORKERS)."
echo "Log: $LOG"
