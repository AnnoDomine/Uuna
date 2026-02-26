#!/bin/bash
# run_tui_tests_stable.sh
# Runs TUI tests 3 times to ensure stability.

set -e

PROJECT_ROOT=$(pwd)
TUI_DIR="$PROJECT_ROOT/Tools/web/tui-node"

echo "🚀 Starting stability test run for TUI (Ink)..."

for i in {1..3}
do
    echo "--------------------------------------------------"
    echo "🏃 Run #$i / 3"
    echo "--------------------------------------------------"
    
    cd "$TUI_DIR"
    if npx vitest run; then
        echo "✅ Run #$i successful."
    else
        echo "❌ Run #$i failed. Aborting."
        exit 1
    fi
done

echo "--------------------------------------------------"
echo "✨ All 3 stability runs passed successfully! ✨"
exit 0
