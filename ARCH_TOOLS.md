# Architektur-Plan: Tools Strukturierung

Dieses Dokument beschreibt die geplante Ziel-Struktur des `Tools/` Verzeichnisses zur Verbesserung der Modularität und Wartbarkeit.

> **Status**: Geplant (Warten auf Abschluss der DuckDB-Migration)
> **Datum**: 2026-02-01

## Verzeichnis-Struktur

### 📂 Tools/core/
*Zentrale Infrastruktur und Basis-Dienste.*
- `db_service.py` - FastAPI Middleware für Master-DB Zugriff.
- `project_init.py` - Initialisierung der Ordnerstrukturen.
- `master_db_init.py` - Setup des DuckDB Master Schemas.
- `research_db_init.py` - Setup der Research-Wissensdatenbank.
- `update_settings.py` - Verwaltung der `Settings.db`.

### 📂 Tools/ingestion/
*Datenbeschaffung und Konvertierung.*
- `sync_wow_db.py` - Multi-threaded Sync von Wago.tools.
- `update_build_registry.py` - Abgleich der verfügbaren WoW-Builds.
- `db2_to_sqlite.py` - Konvertierung von DB2 zu SQLite (Legacy).
- `db2_manifest.json` - Struktur-Manifest für den DB2-Parser.
- `archive_sync.py` - Synchronisation mit externen Archiven.

### 📂 Tools/migration/
*Datenkonsolidierung und Langzeitarchivierung.*
- `migrate_to_master.py` - Überführung von SQLite-Builds in den DuckDB-Master.
- (Zukünftig: `archive_cleanup.py` - Management gezippter Alt-Bestände.)

### 📂 Tools/agents/
*KI-Agenten und Forschungs-Logik.*
- `ai_researcher_agent.py` - Autonomer Archivist für Discovery & Mapping.
- `ai_control.py` - CLI zur Steuerung der KI-Parameter.
- `ai_trainer_dryrun.py` - Simulation von KI-Läufen zu Trainingszwecken.
- `online_researcher.py` - Web-Anbindung für Lore-Checks.
- 📂 `prompts/` - System-Prompts für die verschiedenen KI-Rollen.

### 📂 Tools/analysis/
*Analyse, Mapping und Visualisierung.*
- `feature_extractor.py` - Extraktion statistischer Merkmale aus Tabellen.
- `map_references.py` - Interaktives Mapping von Fremdschlüsseln.
- `cartographer.py` - Generierung von Mermaid ER-Diagrammen.
- `compare_builds.py` - Differenz-Analyse zwischen WoW-Versionen.
- `find_refs.py` / `find_val.py` - Suchwerkzeuge für Referenzen und Werte.
- `mass_indexer.py` - Batch-Indizierung großer Datenmengen.
- 📂 `queries/` - SQL-Templates für komplexe Abfragen.

### 📂 Tools/web/
*Benutzeroberfläche und Präsentation.*
- `db_gui.py` - Hauptanwendung der FastAPI Web-UI.
- 📂 `static/` - CSS, JS und Bilder für die GUI.
- 📂 `templates/` - Jinja2 HTML-Templates.

### 📂 Tools/tests/
*Qualitätssicherung und Sicherheit.*
- `run_qa_test.sh` - Automatisierter Uuna-Rule QA-Lauf.
- `basic_test.py` - Schnelle Funktionsprüfung.
- `test_db_service.py` - Integrationstest für die Middleware.
- `test_sanitization.py` - Prüfung der Datenreinigung.
- `test_sql_security.py` - Validierung gegen SQL-Injection.

---

## Implementierungs-Hinweise
1. **Pfad-Anpassungen**: Bei der Verschiebung müssen alle internen Imports auf absolute Pfade (z.B. `from Tools.core.db_service import ...`) umgestellt werden.
2. **Abhängigkeiten**: Skripte in `analysis/` oder `agents/` sollten primär über den `db_service` kommunizieren, anstatt direkt auf Dateien zuzugreifen.
3. **Ausführung**: Python-Skripte sollten weiterhin über die Root-Venv gestartet werden: `.venv/bin/python3 Tools/subdir/script.py`.
