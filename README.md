# WoW Datamine Toolkit (Retail 12.0)

A specialized toolkit for analyzing and extracting World of Warcraft data, optimized for Patch 12.0 (Midnight Prepatch).

## Features
- **Automated DB2 Sync**: Downloads data directly from Wago.tools for specific builds.
- **SQLite Integration**: Converts complex DB2 structures into easily queryable SQLite tables.
- **Global Search**: Find IDs, text, or flags across the entire database schema.
- **DB Explorer & Command Palette**: Local web interface (FastAPI/HTMX) for browsing data and executing quick actions.
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
   .venv/bin/python3 Tools/sync_wow_db.py 12.0.0.65655
   ```

## Using the Tools (CLI-First Workflow)

Das Toolkit ist für die effiziente Steuerung über das Terminal optimiert. Alle Kernfunktionen können direkt über die Kommandozeile ausgeführt werden.

### 1. Build-Management
```bash
# Registry aktualisieren (Abgleich aller verfügbaren WoW-Builds von Wago.tools)
.venv/bin/python3 Tools/update_build_registry.py

# WoW-Build importieren (Lädt CSVs und erstellt SQLite-Datenbank)
.venv/bin/python3 Tools/sync_wow_db.py 12.0.0.65655
```

### 2. Daten-Analyse & Suche
```bash
# Global Search: Wert (ID, Text) in allen Tabellen finden
# Syntax: python find_val.py <value> [-build=xxx]
.venv/bin/python3 Tools/find_val.py 91423
.venv/bin/python3 Tools/find_val.py "Kun Lai" -build=12.0.0.65655

# Build-Vergleich: Differenz-Analyse zwischen zwei Versionen
# Syntax: python compare_builds.py <old_version> <new_version> [--intermediate]
.venv/bin/python3 Tools/compare_builds.py 12.0.0.65560 12.0.0.65655
```

### 3. Referenz-Mapping
```bash
# Verknüpfung von IDs (QuestID -> QuestV2 etc.)
# Syntax: python map_references.py [build] [--g|--ng]
.venv/bin/python3 Tools/map_references.py 12.0.0.65655
```

### 4. Web-Interface
```bash
# DB Explorer & Command Palette starten (Port 5000)
.venv/bin/python3 Tools/db_gui.py
```
Nutze im Web-Interface die **Command Palette** (Strg+K) für extrem schnelle Navigation zwischen Tabellen und Funktionen.

## Project Structure
- `Tools/`: Python scripts for datamining.
- `Data/`: SQLite databases and import logs.
- `addons/`: Local WoW addons (isolated from datamining).

## Security Note
This toolkit is intended for offline analysis of game data. **Always** run Python scripts within the `.venv` to maintain clean dependency isolation.