#!/bin/bash
# run_all_tests_stable.sh
# Runs both Python and TUI tests 3 times to ensure stability.

set -e

PROJECT_ROOT=$(pwd)
TUI_DIR="$PROJECT_ROOT/Tools/web/tui-node"

echo "🚀 Starting stability test run for ALL components..."

for i in {1..3}
do
    echo "=================================================="
    echo "🏃 Global Run #$i / 3"
    echo "=================================================="
    
    # 1. Python Tests
    echo "🐍 Running Python tests..."
    PYTEST_CMD="pytest"
    
    if command -v uv > /dev/null 2>&1; then
        PYTEST_CMD="uv run pytest"
    elif [ -f ".venv/bin/pytest" ]; then
        PYTEST_CMD=".venv/bin/pytest"
    fi

    if PYTHONPATH=. $PYTEST_CMD Tools/tests/test_db_service.py Tools/tests/test_ai_client.py Tools/tests/test_sanitization.py; then
        echo "✅ Python tests successful."
    else
        echo "❌ Python tests failed. Aborting."
        exit 1
    fi

    # 2. TUI Tests
    echo "⚛️ Running TUI (Ink) tests..."
    cd "$TUI_DIR"
    if npx vitest run; then
        echo "✅ TUI tests successful."
    else
        echo "❌ TUI tests failed. Aborting."
        exit 1
    fi
    cd "$PROJECT_ROOT"
done

echo "=================================================="
echo "✨ All components passed 3 stability runs! ✨"
exit 0
