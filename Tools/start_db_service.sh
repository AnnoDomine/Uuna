#!/bin/bash
# start_db_service.sh
# Startet den FastAPI DB Service robust im Hintergrund

export PATH="$HOME/.local/bin:$PATH"
PYTHON="uv run python"
SCRIPT="Tools/core/db_service.py"
LOG="Data/logs/api.log"

mkdir -p Data/logs
pkill -f db_service.py
sleep 1

echo "--- DB Service Robust Start: $(date) ---" >> "$LOG"

uv run python -c "import subprocess, os; env = os.environ.copy(); env['PYTHONPATH'] = os.getcwd(); subprocess.Popen(['python', '-u', '$SCRIPT'], stdout=open('$LOG', 'a'), stderr=subprocess.STDOUT, start_new_session=True, env=env)"

echo "DB Service wurde im Hintergrund gestartet (start_new_session=True)."
echo "Log: $LOG"
