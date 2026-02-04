#!/bin/bash
# run_qa_test.sh - Automatisiert den Uuna-Rule QA Lauf

# Pfade und Konfiguration
DB_SERVICE="Tools/db_service.py"
AGENT="Tools/ai_researcher_agent.py"
PYTHON=".venv/bin/python3"
LOG_DIR="Data/logs"
DB_LOG="$LOG_DIR/db_service_qa.log"

# Mandats-Parameter
BUILD="7.3.5.25600"
LIMIT=10
export AI_DEBUG=1
export AI_CONCURRENCY=2
export AI_THREADS=2

echo "--- Uuna-Rule QA-Lauf wird vorbereitet ---"

# 1. Alte Prozesse beenden
echo "[1/5] Bereinige alte Prozesse..."
pkill -f "$DB_SERVICE" || true
pkill -f "$AGENT" || true
sleep 1

# 2. DB-Service starten
echo "[2/5] Starte DB-Service..."
nohup $PYTHON $DB_SERVICE > "$DB_LOG" 2>&1 &
DB_PID=$!

# 3. Auf Port warten
echo "[3/5] Warte auf DB-Service (Port 8001)..."
MAX_RETRIES=15
READY=0
for i in $(seq 1 $MAX_RETRIES); do
  if curl -s http://127.0.0.1:8001/query -d '{"sql":"SELECT 1"}' -H "Content-Type: application/json" | grep -q "results"; then
    echo "      DB-Service ist BEREIT."
    READY=1
    break
  fi
  echo "      Warte... ($i/$MAX_RETRIES)"
  sleep 2
done

if [ $READY -eq 0 ]; then
  echo "FEHLER: DB-Service konnte nicht gestartet werden. Letzte Log-Zeilen:"
  tail -n 10 "$DB_LOG"
  kill $DB_PID 2>/dev/null
  exit 1
fi

# 4. Agent starten
echo "[4/5] Starte QA-Lauf (Build: $BUILD, Limit: $LIMIT)..."
$PYTHON $AGENT --start "$BUILD" --end "$BUILD" --limit $LIMIT
AGENT_EXIT_CODE=$?

# 5. Aufräumen
echo "[5/5] Beende DB-Service (PID $DB_PID)..."
kill $DB_PID 2>/dev/null
wait $DB_PID 2>/dev/null

echo "----------------------------------------"
if [ $AGENT_EXIT_CODE -eq 0 ]; then
  echo "ERFOLG: QA-Lauf abgeschlossen."
else
  echo "FEHLER: Agent wurde mit Code $AGENT_EXIT_CODE beendet."
fi
exit $AGENT_EXIT_CODE
