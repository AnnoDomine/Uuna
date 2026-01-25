# WoW Datamine Toolkit (Retail 12.0)

A specialized toolkit for analyzing and extracting World of Warcraft data, optimized for Patch 12.0 (Midnight Prepatch).

## Features
- **Automated DB2 Sync**: Downloads data directly from Wago.tools for specific builds.
- **SQLite Integration**: Converts complex DB2 structures into easily queryable SQLite tables.
- **Global Search**: Find IDs, text, or flags across the entire database schema.
- **DB Explorer**: Local web interface (Flask) for browsing data.
- **Version Management**: Support for version-specific databases to handle schema changes between WoW builds.

## Installation & Setup

1. **Set up Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

2. **Synchronize Database**:
   ```bash
   .venv/bin/python3 Tools/sync_wow_db.py 12.0.0.65560
   ```

## Using the Tools

### Global Search
Search for an ID (e.g., Quest ID) in all tables:
```bash
.venv/bin/python3 Tools/find_val.py 91423
```

### Start DB Explorer
Starts a local web interface at `http://localhost:5000`:
```bash
.venv/bin/python3 Tools/db_gui.py
```

## Project Structure
- `Tools/`: Python scripts for datamining.
- `Data/`: SQLite databases and import logs.
- `addons/`: Local WoW addons (isolated from datamining).

## Security Note
This toolkit is intended for offline analysis of game data. **Always** run Python scripts within the `.venv` to maintain clean dependency isolation.
