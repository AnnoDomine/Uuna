#!/bin/bash
# Automatically find the first 7.x and last 8.x build
START_V=$(ls Data/dbs/WoW_Data_7.*.db 2>/dev/null | head -n 1 | sed -n 's/.*WoW_Data_\(.*\)\.db/\1/p')
END_V=$(ls Data/dbs/WoW_Data_8.*.db 2>/dev/null | tail -n 1 | sed -n 's/.*WoW_Data_\(.*\)\.db/\1/p')

if [ -z "$START_V" ] || [ -z "$END_V" ]; then
    echo "Error: Could not find local 7.x or 8.x databases."
    exit 1
fi

echo "--- Starting Mass Indexing for Legion & BfA ---"
echo "Range: $START_V to $END_V"
echo "-----------------------------------------------"

.venv/bin/python3 Tools/mass_indexer.py --start "$START_V" --end "$END_V"
