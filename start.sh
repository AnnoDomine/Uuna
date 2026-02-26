#!/bin/bash

# Uuna WoW Datamine Toolkit - Universal Start Script
# Version: 0.10.0-alpha

# Colors for better visibility
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 Starting Uuna WoW Datamine Toolkit (v0.10.0-alpha)...${NC}"

# 1. Verification
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: 'uv' is not installed. Please run init.sh first.${NC}"
    exit 1
fi

if ! command -v pnpm &> /dev/null; then
    echo -e "${RED}Error: 'pnpm' is not installed. Please install Node.js 24 and pnpm.${NC}"
    exit 1
fi

# 2. Start Backend 1: DB Service (Port 8002)
echo -e "${GREEN}📦 Starting DB Service (DuckDB Gateway)...${NC}"
uv run python -m uvicorn Tools.core.db_service:app --port 8002 --host 127.0.0.1 > Data/logs/db_service_start.log 2>&1 &
DB_PID=$!

# 3. Start Backend 2: Orchestra API (Port 8001)
echo -e "${GREEN}🧠 Starting Orchestra API (Agent Logic)...${NC}"
uv run python -m uvicorn Tools.core.api.main:app --port 8001 --host 127.0.0.1 > Data/logs/orchestra_api_start.log 2>&1 &
API_PID=$!

# Function to kill backends on exit
cleanup() {
    echo -e "
${YELLOW}🛑 Shutting down services...${NC}"
    kill $DB_PID $API_PID 2>/dev/null
    exit
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM

# 4. Wait for APIs to be healthy
echo -e "${YELLOW}⏳ Waiting for APIs to initialize...${NC}"
MAX_RETRIES=15
COUNT=0
while ! curl -s http://127.0.0.1:8001/health > /dev/null; do
    sleep 1
    COUNT=$((COUNT + 1))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo -e "${RED}Error: APIs failed to start in time. Check Data/logs/ for details.${NC}"
        cleanup
    fi
done
echo -e "${GREEN}✅ APIs are online!${NC}"

# 5. Start Frontend: TUI
echo -e "${CYAN}🖥️  Launching TUI...${NC}"
cd Tools/web/tui-node || exit
pnpm start

# After TUI exits, trigger cleanup
cleanup
