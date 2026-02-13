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
    REPORTS_DIR="$PROJECT_ROOT/Data/test-reports"
    mkdir -p "$REPORTS_DIR"
    
    if command -v uv > /dev/null 2>&1; then
        PYTEST_CMD="uv run pytest"
    elif [ -f ".venv/bin/pytest" ]; then
        PYTEST_CMD=".venv/bin/pytest"
    fi

    PYTEST_ARGS="Tools/tests/"
    if [ "$GENERATE_REPORTS" = "true" ]; then
        PYTEST_ARGS="$PYTEST_ARGS --junitxml=$REPORTS_DIR/python-run-$i.xml"
    fi

    if PYTHONPATH=. $PYTEST_CMD $PYTEST_ARGS; then
        echo "✅ Python tests successful."
    else
        echo "❌ Python tests failed. Aborting."
        exit 1
    fi

    # 2. TUI Tests
    echo "⚛️ Running TUI (Ink) tests..."
    cd "$TUI_DIR"
    VITEST_ARGS="run"
    if [ "$GENERATE_REPORTS" = "true" ]; then
        VITEST_ARGS="$VITEST_ARGS --reporter=junit --outputFile=$REPORTS_DIR/tui-run-$i.xml"
    fi

    # Use pnpm if available, otherwise npx
    if command -v pnpm > /dev/null 2>&1; then
        if pnpm exec vitest $VITEST_ARGS; then
            echo "✅ TUI tests successful."
        else
            echo "❌ TUI tests failed. Aborting."
            exit 1
        fi
    else
        if npx vitest $VITEST_ARGS; then
            echo "✅ TUI tests successful."
        else
            echo "❌ TUI tests failed. Aborting."
            exit 1
        fi
    fi
    cd "$PROJECT_ROOT"
done

echo "=================================================="
echo "✨ All components passed 3 stability runs! ✨"
exit 0
