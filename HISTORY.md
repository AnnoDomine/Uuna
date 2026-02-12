# Projekt History - WoW Datamine Toolkit

## [0.9.11] - 2026-02-12 - "The Relay-Race & Blind Wisdom"

### Added
- **Atomisierte Skill-Sets**: Einführung einer Markdown-basierten "Ausbildung" für alle 9 Agenten. Jeder Agent weiß nun durch `get_my_skills` exakt, welche prozeduralen Schritte für seine Aufgaben notwendig sind.
- **Event-Relais-Logik**: Das System wurde von flüchtigen Funktionsaufrufen auf eine lückenlose Kette von Event-IDs ("Fackellauf") umgestellt. Dies garantiert eine 100%ige Auditierbarkeit jeder Entscheidung.
- **Vektor-Gedächtnis (RAG)**: Integration von DuckDB VSS als Langzeitgedächtnis. Agenten können nun semantisch nach Mustern in früheren Forschungsaufträgen suchen.
- **Internationalisierung**: Dynamische Lokalisierung der Nutzer-Kommunikation. Der Librarian beherrscht nun mehrere Sprachen (getestet: Deutsch, Englisch, Japanisch) basierend auf den System-Settings.
- **Blind Scoring**: Vollständige Isolation der Bewertungsebene. Agents und der Courier haben keinen Zugriff auf absolute Punktzahlen (Max Potential), was Manipulationen des Systems verhindert.

### Changed
- **Rollen-Konsolidierung**: Überführung des "Data Engineer" in den Archivist und des "Senior Critic" in die Sages für ein schlankeres 9-Agenten-Modell.
- **Chirurgisches Prompting**: Umstellung aller KI-Anweisungen auf lokale Tool-Prompts mit Verweisen auf die neuen Skill-Files.

### Fixed
- **Wiki-Scraping**: Behebung von 403-Fehlern beim Zugriff auf Warcraft Wiki durch Referer-Header-Injection.
- **Integrität**: Beseitigung von Redundanzen in der Tool-Hierarchie (Global vs. Agent-spezifisch).

## [0.9.10] - 2026-02-11 - "The API Gateway & Parallel Ingestion"

### Added
- **API-First Architektur**: Einführung des `db_service.py` als zentrales FastAPI-Gateway. Alle Schreib- und Lesezugriffe auf den DuckDB-Master erfolgen nun über eine entkoppelte Schnittstelle.
- **Zentraler DB-Client**: Implementierung der `DBClient`-Klasse in `Tools/core/db_client.py`. Dies ermöglicht allen Python-Tools einen einheitlichen, Thread-sicheren Zugriff ohne direkte Datei-Sperren.
- **Multi-Worker Ingestion**: Der `master_ingester.py` unterstützt nun parallele Tabellen-Downloads und -Imports mittels `ThreadPoolExecutor`.
- **Isolierte Workspaces**: Nutzung von eindeutigen temporären Tabellen (`tmp_table_build_version`) pro Worker, um Kollisionen bei parallelen Schreibvorgängen zu verhindern.
- **Robuste Daten-Pipeline**: Erweiterung des CSV-Parsings um `ignore_errors=True` und `null_padding=True`, um strukturelle Fehler in Remote-Daten (z.B. `NeighborhoodPlot`) abzufangen.
- **Hintergrund-Resilienz**: Upgrade der Start-Skripte auf eine Python-basierte Prozess-Abkopplung (`start_new_session=True`), die Terminal-unabhängig stabil läuft.

### Changed
- **Entkoppelung**: Umstellung von `feature_extractor.py` und `master_ingester.py` auf API-Zugriff via `DBClient`.
- **Modul-Auflösung**: Optimierung des `PYTHONPATH` Handlings, um das `Tools`-Paket systemweit verfügbar zu machen.

### Fixed
- **Schema Evolution Race Conditions**: Case-insensitive Spalten-Prüfung verhindert Abstürze bei unterschiedlicher Groß-/Kleinschreibung in neuen Builds.
- **API Debugging**: Integration von Traceback-Printing im `/execute` Endpoint zur schnellen Fehleranalyse im `api.log`.

## [0.9.9] - 2026-02-08 - "The Responsive Layout & Semantic Memory"

### Added
- **Dynamic Full-Screen TUI**: Einführung des `useTerminalDimensions` Hooks. Das Interface skaliert nun verzögerungsfrei bei jeder Größenänderung des Terminalfensters.
- **Enterprise Layout-Stabilität**: Umstellung auf eine "Fixed-Fluid" Architektur. Jedes UI-Element hat nun strikt definierte Maße (statisch oder prozentual), was Layout-Sprünge und Verschiebungen eliminiert.
- **Vector Memory Explorer**: 
  - Funktionale semantische Suche im Agenten-Gedächtnis.
  - Zwei-Spalten-Layout mit Echtzeit-Filterung nach Rollen (Librarian, Archivist, etc.).
  - Anzeige der Match-Qualität (Similarity Score) und Metadaten-Herkunft.
- **Scoring Board Optimierung**: Redesign der Übersicht in ein Side-by-Side Modell (Agent-Stats vs. Scoring-History) für bessere Lesbarkeit auf breiten Terminals.
- **Interaktives Wiki & Help**: 
  - **Wiki**: Markdown-Inhalte sind nun fokussierbar und scrollbar.
  - **Help**: Neue statische Seite für CLI-Interaktionshilfe mit Keybinding-Tabelle.
- **Python-Backend Synchronisierung**: Anpassung des `VectorManager` an das Frontend (id, role, score Felder) für nahtlose Datenflüsse.

### Changed
- **Struktur**: Trennung der "Help"-Logik von der "Wiki"-Dokumentation.
- **Komponenten**: `ScrollableSelection` und `ScrollArea` wurden für maximale Flexibilität innerhalb von Container-Layouts optimiert.

### Fixed
- **Scroll-In-View**: Fokussierte Listenelemente werden nun zuverlässig in den sichtbaren Bereich geschoben.
- **Typ-Sicherheit**: Finale Beseitigung aller `@ts-ignore` Altlasten durch korrekte API-Interface-Definitionen.

## [0.9.8] - 2026-02-08 - "The React TUI & Enterprise Standards"

### Added
- **Node.js/Ink Migration**: Radikaler Technologiewechsel des User-Interfaces von Python Textual zu **React (Ink)**. Dies ermöglicht echtes Flexbox-Layout und eine stabilere Render-Engine (Yoga).
- **Enterprise-Standard Architektur**: Einführung eines strikten Frontend-Patterns:
  - **Atomic Design**: Hierarchische Trennung in Atoms, Molecules, Organisms und Pages.
  - **Logic Decoupling**: Konsequente Nutzung von Custom Hooks (`.hooks.ts`) zur Trennung von Business-Logik und UI.
  - **Typ-Sicherheit**: Volle TypeScript-Integration ohne Kompromisse (strikte `@ts-ignore` Sperre).
- **Global State & Immutability**: Einsatz von **Zustand** für das app-weite State-Management und **Immer** für sichere, mutierbare State-Updates via `draft`.
- **Scoped Focus System**: Entwicklung des `useScopedInput` Hooks zur exklusiven Steuerung von UI-Arealen. Verhindert Tasten-Kollisionen zwischen Sidebar und Content.
- **Backend Orchestration**: Vollautomatisiertes Management des Python-Backends (FastAPI/Uvicorn):
  - **Auto-Start**: TUI startet das Backend bei Bedarf selbstständig.
  - **Health-Checks**: Periodische Überprüfung der API-Verfügbarkeit.
  - **Clean Exit**: Automatisches Beenden aller Hintergrundprozesse beim Schließen der TUI.
- **Local Patching Framework**: Neues `Patches/` System zur Einbindung und Reparatur externer Ink-Addons (z.B. Umstellung von CommonJS auf ESM für `ink-markdown`).
- **Virtualized Content Scrolling**: Implementierung von `ScrollArea` und `ControlledScrollView` für flüssige Navigation in großen Listen und Dokumentationen.
- **Biome Integration**: Einführung von **Biome** als ultraschneller Ersatz für ESLint und Prettier (Format & Lint on Save).

### Changed
- **Navigation Flow**: Umstellung auf ein zustandsgesteuertes Switch-Pattern für blitzschnelle Seitenwechsel.
- **StatusBar Revamp**: Umbau zu einem dynamischen, daten-getriebenen Organismus mit Echtzeit-Indikatoren.
- **Settings & Tasks Integration**: Überführung der zentralen Mining-Funktionen in die neue React-Architektur.

### Fixed
- **Terminal Rendering Bugs**: Behebung von Layout-Verschiebungen und korrupten Zeichen-Zellen durch Wechsel auf React-Komponenten.
- **MaxListeners Warnings**: Optimierung des Keyboard-Listener-Managements zur Vermeidung von Memory Leaks.

## [0.9.5] - 2026-02-01 - "The Library Orchestration & Scoring Logic"

### Added
- **Library Multi-Agent Architecture**: Einführung eines spezialisierten Orchestrierungssystems mit klar definierten Rollen:
  - **Librarian**: Zentrales Nutzer-Interface und Wissens-Synthese.
  - **Courier**: Herzstück der Orchestrierung, managt Task-Routing und Queue-Priorisierung.
  - **Archivist**: Experte für den DuckDB-Master und Daten-Relationen.
  - **Expedition Group**: Spezialist für Online-Lore-Research (Wowhead, Wago).
  - **Sentinel**: Middleware für Daten-Sanitization und SQL-Sicherheit.
  - **Sages**: Finale Instanz zur Wissensverifizierung (Gatekeeper).
- **Advanced Scoring Framework**: Einführung einer hocheffizienten Reinforcement-Logik zur KI-Qualitätssicherung:
  - **The Tinker**: Bewertet quantitativ die "Arbeitsschwere" (Max Potential) ohne Kontext-Bias.
  - **The Observer**: Strenge qualitative Bewertung (Actual Score) inkl. Honesty-Check (Abgleich mit der Agent-Confidence).
  - **Cooperated Learning**: Abschluss-Scoring basierend auf Team-Synergie (60% CPP) und Prozess-Effizienz (40% Task-Score).
- **Human-in-the-Loop Training**: Implementierung von `AI_PHASE_TRAINING` zur Kalibrierung der "Richter" mittels fiktiver Szenarien und manuellem User-Feedback.
- **Master Ingester Pipeline**: Neues hocheffizientes Tool für den direkten Import von Wago.tools in DuckDB:
  - **MD5 Content Deduplication**: Identische Datensätze über 1500+ Builds werden physisch nur einmal gespeichert.
  - **Unified Build Data Map**: Zentrale Verknüpfung von Builds zu deduplizierten Inhalts-Hashes.
- **Systematic Project Wiki**: Aufbau eines RPG-thematisierten Benutzerhandbuchs in `docs/wiki/` (English First) mit:
  - Detaillierten Rollenbeschreibungen und Architektur-Diagrammen.
  - SVG-basierten Agenten-Portraits zur Gamification.
  - Installations- und Ingestion-Guides.
- **AI PATCH System**: Etablierung eines Best-Practice-Katalogs in `AGENT.md` zur Vermeidung technischer Fallstricke (Process Management, SQL Injection, JSON Parsing).

### Changed
- **Tools Reorganization**: Vollständige Modularisierung des `Tools/` Verzeichnisses in `core`, `ingestion`, `analysis`, `agents`, `web` und `tests`.
- **Log-Standardisierung**: Einführung eines einheitlichen, hoch-informativen Log-Schemas für alle Systemkomponenten.
- **SQL Outsourcing**: Konsequente Trennung von Logik und Daten durch Externalisierung aller SQL-Abfragen in das `queries/` Verzeichnis.
- **Storage Optimization**: Auslagerung von Legacy-Backups (SQLite) auf externen Cold Storage; Optimierung der lokalen SSD für den DuckDB-Master.

### Fixed
- **Stability Break-through**: Behebung von "Missing Table" Warnungen durch direkten CSV-Stream-Import von Wago.tools.
- **Background Process Resilienz**: Lösung von Terminal-Session-Abbrüchen durch entkoppelte Python-Sessions (`start_new_session=True`).
- **DuckDB Constraint Fix**: Korrektur der Auto-Increment-Syntax für Sequenzen und Primärschlüssel.

---

## [0.9.0] - 2026-02-01 - "The Master Archive & DuckDB Integration"
### Added
- **DuckDB Master Integration**: Umstellung des zentralen Speichers auf **DuckDB** (`WoW_Master.duckdb`) zur Handhabung hunderter Millionen von Datensätzen bei minimalem Speicherbedarf.
- **Unified Middleware (`db_service.py`)**: Implementierung eines asynchronen FastAPI-Dienstes zur Orchestrierung des Master-DB-Zugriffs für alle KI-Agenten und Tools.
- **Mass-Migration & Archiving**: Neues hocheffizientes Tool `migrate_to_master.py` mit:
  - **6-Core Parallelisierung**: Gleichzeitige Migration von 6 Builds über DuckDB-Worker.
  - **Auto-Archivierung**: Automatisches Zippen und Verschieben integrierter SQLite-Files nach `Data/backups/archived_sqlite/`.
  - **Heuristische Filterung**: Intelligente Erkennung unvollständiger Builds zur Vermeidung korrupter Archiv-Daten.
- **Uuna-Rule QA Framework**: Mandatierung eines automatisierten Test-Laufs (`run_qa_test.sh`) vor jeder größeren Änderung, um die Mapping-Integrität sicherzustellen.
- **Persistent Knowledge Migration**: Erfolgreiche Überführung von Legacy-Wissen (Mappings, Entdeckungen) in das neue Master-Schema.

### Changed
- **Performance-Boost**: Reduzierung der Mapping-Validierungszeiten durch DuckDB-Indizierung und asynchrones ID-Checking.
- `ai_researcher_agent.py`: Agent nutzt nun die Middleware-API statt direkter SQLite-Verbindungen für verbesserte Resilienz.
- **Logging-Standardisierung**: Alle Logs werden nun zentral in `Data/logs/` strukturiert erfasst.

### Fixed
- Behebung von DuckDB-Startup-Problemen durch Korrektur falscher PRAGMA-Kommandos und Umstellung auf Thread-sichere Connections.
- Stabilisierung paralleler Schreibzugriffe durch Entfernung blockierender globaler Locks zugunsten nativer DuckDB-Concurrency.

---

## [0.8.0] - 2026-01-31 - "The AI Brain Update"
### Added
- **Local LLM Orchestration**: Nahtlose Integration von **Ollama** zur Ausführung lokaler Modelle (**Qwen 3 8B**).
- **Research Knowledge DB**: Implementierung einer zentralen SQLite-Wissensdatenbank zur build-übergreifenden Speicherung von KI-Erkenntnissen.
- **Archivist Agent**: Entwicklung eines autonomen Forschungs-Agenten mit einem zweistufigen Prozess:
  - **Discovery Phase**: Semantische Analyse von Inhalten (Lore, Bosse, Dialog-Kontext).
  - **Mapping Phase**: Strukturelle Zuordnung unbekannter Spalten zu Datenbank-Tabellen.
- **AI Control CLI**: Neues Steuerungs-Tool `ai_control.py` zur Verwaltung von KI-Einstellungen (Threads, Cooldown, Limits) und Überwachung des Lernfortschritts.
- **Multi-Build Training**: Fähigkeit des Agenten, chronologisch durch Builds zu lernen und Wissen durch Wiederholung (`confirmations`) zu festigen.
- **Self-Criticism System**: Implementierung eines "Senior Data Critic" Layers, der KI-Vorschläge auf logische Konsistenz prüft und Fehl-Mappings verhindert.
- **Hardware-Optimierung**: Unterstützung für GPU-Offloading (RTX 4070 Ti) und parallele Abfragen (`AI_CONCURRENCY`) mit integrierter Hardware-Bremse.
- **Discovery Logging**: Neue Tabelle `ai_discoveries` für inhaltliche Funde, die über das technische Mapping hinausgehen.

### Changed
- `feature_extractor.py`: Umstellung von massivem JSON-Output auf effiziente SQLite-Speicherung in der Research-DB.
- `README.md` & `AGENT.md`: Umfassende Aktualisierung mit Fokus auf KI-gestütztes Research und CLI-First Workflow.
- Erhöhung der Stabilität durch robustes JSON-Decoding und automatische Begriffsreinigung (`clean_confidence`).

### Fixed
- Behebung von Timeouts bei großen Abfrage-Batches durch optimiertes Thread-Management.
- Korrektur von Abstürzen bei inkonsistenten KI-Antwortformaten via `robust_json_decode`.

---

## [0.6.0] - 2026-01-25 - "The GUI Era"
### Added
- **FastAPI + HTMX GUI**: Vollständig neue Web-Oberfläche mit Explorer, Sync-Management und Build-Vergleich.
- **Real-time Logging**: SSE (Server-Sent Events) Integration für Live-Sync-Logs im Browser.
- **Theme Support**: Implementierung von Light/Dark Mode via Bootstrap 5.3 (persistant gespeichert).
- **Settings UI**: Generische Einstellungsseite zur Konfiguration von Workern, Mapping-Verhalten und Design.
- **Project Init**: Automatisierte Initialisierung der Ordnerstruktur und Datenbanken (`project_init.py`).
- **Concurrent Safety**: Globaler Sync-Lock zur Vermeidung paralleler Datenbank-Operationen in der GUI.

### Changed
- Migration von Flask zu FastAPI für verbesserte asynchrone Performance.
- `db_gui.py` nutzt nun HTMX Partials zur Reduzierung des Netzwerk-Traffics.
- Refactoring der Build-Registrierung zur Speicherung von Download-Status und Sync-Zeitstempeln.

### Fixed
- UI-Nesting-Fehler beim Navigieren durch die GUI behoben.
- Korrektur der Datenbank-Schemata bei Alt-Installationen via automatischer Migration.

---

## [0.5.0] - 2026-01-25 - "The Performance & Intelligence Update"
### Added
- **Build Registry**: Zentrale `Build_Registry.db` speichert nun alle verfügbaren WoW-Builds von Wago.tools via API.
- **Settings System**: `Settings.db` zur Konfiguration globaler Tool-Parameter (z.B. `workers`).
- **Parallel Sync**: `sync_wow_db.py` unterstützt jetzt Multi-Threading (ThreadPoolExecutor) für massiv beschleunigte Downloads und Imports.
- **SQLite Performance**: Aktivierung von WAL-Mode und Synchronous-Optimierungen für parallele Schreibvorgänge.
- **Global Column Learning**: `map_references.py` lernt nun global, welche Spaltennamen zu welchen Tabellen gehören.
- **Build Continuity**: Automatischer Import von Mapping-Entscheidungen aus chronologisch vorherigen Builds.
- **Skip Shortcuts**: Neue Option `0a` (Skip All) im Mapping-Prozess zur schnellen Fertigstellung von Sitzungen.
- **Auto-Automation**: Neue Settings für vollautomatisches globales Mapping und Auto-Skip.

### Changed
- `sync_wow_db.py`: Robusteres CSV-Parsing mit automatischer Trennzeichen-Erkennung (Komma vs. Semicolon).
- `compare_builds.py`: Integration der Build-Registry und Support für On-the-fly Downloads fehlender Vergleichs-Builds.
- `map_references.py`: Code-Cleanup und Entfernung von Redundanzen.

### Fixed
- Behebung von Header-Korruption ("ID;Name") durch verbesserte Delimiter-Logik.
- Korrektur von Fehl-Mappings bei inkonsistenten Spaltennamen über verschiedene WoW-Versionen hinweg.

---

## [0.4.0] - 2026-01-25 - Referenz-Mapping & Interaktivität
### Added
- `Tools/map_references.py`: Komplett überarbeitet für interaktives Mapping.
- Build-spezifische Benutzer-Mappings (`_user_map.json`) zur Vermeidung von Fehlzuordnungen zwischen WoW-Versionen.
- Fuzzy-Matching und Substring-Suche für Tabellenvorschläge ohne künstliches Limit.
- Erkennung und Warnung bei korrupten Spaltennamen (Semikolon-Importfehler).

### Changed
- `AGENT.md`: Dokumentation der neuen Tool-Suite und des Referenz-Workflows.
- `Tools/map_references.py`: `resolve_table_name` verbessert (Alias-Support für QuestV2, SpellName, etc.).

### Fixed
- Problem mit unübersichtlichen Referenz-Abfragen bei fehlerhaftem DB-Import behoben.
- Trennung von globalen und build-spezifischen Mapping-Entscheidungen.

## [Frühere Sitzungen]
- Initialisierung der Tool-Suite (`sync_wow_db.py`, `find_val.py`).
- Aufbau der SQLite-Datenbankstruktur für WoW 12.0 Retail.
- Implementierung des Flask-basierten DB-Explorers (`db_gui.py`).
