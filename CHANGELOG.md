# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.14] - 2026-02-18
### Added
- **Automated Setup Script**: New `init.sh` for one-click environment preparation, including dependency checks for uv, Node.js, and Ollama.
- **Hardware Optimization Engine**: Introduced `hardware_analyzer.py` and `manage.py optimize` command to automatically configure AI settings based on CPU, RAM, and GPU availability.
- **AI Acceleration Modes**: Added support for explicit `CPU`, `GPU`, and `Hybrid` (Both) execution modes.
- **TUI Component Testing**: Established a comprehensive unit test suite for all TUI organisms and hooks (25+ test files).

### Changed
- **TUI Atomic Refactor**: Completed the transition to a full Atomic Design architecture, extracting complex business logic from UI components into custom hooks.
- **Dynamic AI Client**: Refactored `AIClient` to load hardware settings from DuckDB with a 5-minute TTL cache for improved performance and flexibility.
- **Documentation Overhaul**: Updated Wiki requirements and contributor guides with detailed AI model setup instructions.

## [0.9.13] - 2026-02-14

### Added

- **Task Inspector Page**: New 3-column interactive monitoring interface in the TUI for real-time tracking of research tasks, events, and scoring.
- **Atomic Design Refactor**: Complete modularization of the Tasks page into `TaskList`, `EventList`, and `TaskDetails` organisms.
- **Global DB Instance**: Introduced `shared_db_instance.py` providing a centralized `db` object, eliminating the need to pass `db_client` through every tool signature.
- **Scoped Input Integration**: Replaced legacy focus handling in `Home.tsx` with `useScopedInput` for consistent navigation across all pages.
- **Enhanced Task Metadata**: New API endpoints for retrieving granular event data and task-specific scoring logs.

### Changed

- **Tool Standardisation**: Refactored all 40+ system, research, and analysis tools to support automated docstring parsing for the new KI-orchestration flow.
- **Non-Blocking AI Chat**: Integrated `run_in_threadpool` in the AI router to keep the TUI health-check responsive during long-running LLM operations.
- **Test Suite Modernization**: Updated the entire test suite (68+ tests) to support global DB mocking and the new tool signatures.

### Fixed

- **API Health False-Offlines**: Resolved UI lock-ups by offloading blocking synchronous AI calls to background threads.
- **DuckDB Catalog Errors**: Fixed table name resolution in the build registry queries.

## [0.9.12] - 2026-02-13

### Added

- **Python 3.12 Migration**: Upgraded the core environment to Python 3.12 for improved performance and modern feature support.
- **uv Package Manager**: Replaced `pip` with **uv** for lightning-fast dependency management and reliable `uv.lock` builds.
- **Standardized pyproject.toml**: Centralized all project metadata and dependencies into a modern PEP 621 compliant file.
- **TUI E2E Testing**: Established a comprehensive Vitest-based testing suite for the React/Ink TUI with navigation simulation.
- **Global Stability Guard**: New `run_all_tests_stable.sh` script ensuring all components pass 3 consecutive runs before deployment.

### Changed

- **CI/CD Pipeline**: Updated GitHub Actions to utilize Python 3.12 and `uv sync` for significantly faster build times.
- **Shell Tools**: Refactored all `.sh` start scripts to prefer `uv run` for consistent environment execution.
- **Core Mandates**: Updated `AGENT.md` to establish Python 3.12 and `uv` as the new development standards.

### Removed

- **Legacy Textual TUI**: Removed the outdated Python-based TUI to focus exclusively on the superior React (Ink) implementation.

## [0.9.11] - 2026-02-12

### Added

- **Multi-Agent Skill-Sets**: Implemented atomic Markdown-based procedural knowledge for all 9 agent roles in `Tools/agents/skills/`.
- **Event-Relay Orchestration**: Transitioned the entire system from direct calls to a robust "Relay-Race" protocol using Event IDs.
- **Semantic Vector Memory**: Integrated a dedicated DuckDB VSS database for long-term pattern recognition and lore storage.
- **Dynamic Localisation**: Introduced a global `localisation` setting allowing the Librarian to communicate in any language (German, Japanese, etc.) while maintaining English for internal logic.
- **Standardized Identity Headers**: All KI prompts now include a persistent identity block referencing their specific skill-sets.
- **New Infrastructure Tools**:
  - Global: `get_my_skills`, `get_task_context`, `get_event_data`, `log_event_reasoning`.
  - Courier: `create_task_event`, `update_task_status`, `get_role_capabilities`.
  - Audit: `check_logical_consistency`, `grant_final_verdict`, `assess_complexity`.

### Changed

- **Unified Agent Identities**: Integrated legacy "Data Engineer" and "Senior Critic" roles into the Archivist and Sages specialists.
- **Information Isolation**: Implemented "Blind Scoring" where agents never see absolute points, only success percentages.
- **Tool-Prompt Locality**: Prompts are now stored directly within their respective tool directories for better modularity.

### Fixed

- **Wiki Access (403)**: Fixed 403 Forbidden errors when fetching data from Warcraft Wiki by implementing proper Referer headers.
- **Scoring Manipulation**: Decoupled potential score calculation from the orchestration layer to prevent incentive gaming.
- **DuckDB Path Resolution**: Improved absolute path handling in the API layer to prevent database initialization errors in sub-processes.

## [0.9.10] - 2026-02-11

### Added

- **API-First Database Architecture**: Introduced `db_service.py` as a centralized FastAPI gateway for all database operations, eliminating file-locking issues.
- **Unified DB Client**: New `DBClient` class in `Tools/core/db_client.py` providing a standardized interface for Python tools (Ingester, Indexer) to communicate via API.
- **Multi-Worker Ingestion Engine**: Refactored `master_ingester.py` to support parallel table ingestion with configurable `MAX_WORKERS`.
- **Race-Condition Protection**: Implemented unique temporary table naming (`tmp_table_build_version`) and case-insensitive schema evolution checks.
- **Robust CSV Parsing**: Enhanced `read_csv_auto` calls with `ignore_errors=True` and `null_padding=True` to handle malformed data from remote sources.
- **Process Management 2.0**: Updated background start scripts (`start_db_service.sh`, `start_master_ingester.sh`) using `start_new_session=True` for terminal-independent execution.

### Changed

- Migrated `feature_extractor.py` and `master_ingester.py` from direct DuckDB connections to `DBClient` API access.
- Optimized `PYTHONPATH` handling in start scripts to ensure proper module resolution for the `Tools` package.

### Fixed

- **Schema Evolution Crashes**: Fixed `CatalogError` caused by case-sensitive column name mismatches (e.g., `CornerStonePosition_0` vs `CornerstonePosition_0`).
- **Logger Syntax**: Corrected `base_logger.log` calls to `base_logger.info` in the ingestion pipeline.
- **API Stability**: Improved error handling in `db_service.py` with explicit traceback printing for `/execute` endpoint.

## [0.9.9] - 2026-02-08

### Added

- **Full-Screen Dynamic Layout**: Implemented `useTerminalDimensions` hook to automatically adapt the TUI to any terminal window size in real-time.
- **Enterprise Layout Engine**: Switched to a "Fixed-Fluid" architecture using explicit dimensions (`width`/`height`) and percentages for maximum structural stability.
- **Vector Memory Explorer**: Fully functional semantic search interface with dual-column layout, role-based filtering, and real-time similarity score visualization.
- **Improved Scoring Board**: Redesigned side-by-side view for agent performance metrics and historical scoring logs.
- **Enhanced Wiki System**: Integrated focus-enabled scrolling for markdown content and semantic link parsing within the documentation.
- **Static Help Page**: Dedicated help system with topic navigation and keybinding reference (Global vs. Contextual keys).
- **Backend API Sync**: Synchronized Python backend (`VectorManager`) with TypeScript frontend types (id, role, score fields).

### Changed

- Refactored `index.tsx` to use a robust container-based layout with proportional sizing.
- Renamed "Help" menu to "Wiki" and created a separate "Help" system for CLI usage.
- Optimized `ScrollableSelection` to support 100% parent container filling.

### Fixed

- **Layout Stability**: Eliminated unpredictable shifting by using strict box dimensioning.
- **Scrolling Sync**: Fixed issues where focused items didn't automatically scroll into view within lists.
- **Focus Collisions**: Improved `useScopedInput` to handle complex nested focus scenarios (e.g., inside ScrollViews).

## [0.9.8] - 2026-02-08

### Added

- **React-powered TUI**: Complete migration from Python Textual to a Node.js/React (Ink) stack for superior layout stability and developer experience.
- **Enterprise Architecture**: Implementation of a strict Atomic Design pattern (Atoms, Molecules, Organisms, Pages) with separated logic (hooks, types, constants).
- **Global State Management**: Integration of **Zustand** for global app state and **Immer** for safe, immutable local state updates.
- **TypeScript Integration**: 100% type-safety across the frontend with a strict prohibition of `@ts-ignore`.
- **Scoped Focus & Input**: Developed a custom `useScopedInput` hook to eliminate keyboard collisions and manage area-specific interactions (Navigation vs. Content).
- **Backend Lifecycle Orchestration**: Automated starting, stopping, and health-checking of the Python FastAPI backend directly from the TUI.
- **Virtualized Scrolling**: Implemented robust `ScrollArea` and `ControlledScrollView` components for high-performance terminal scrolling.
- **Local Patch System**: Established a `Patches/` directory for hosting and fixing unmaintained or CJS-based Ink addons (e.g., `ink-markdown`).
- **Biome Tooling**: Integrated **Biome** for lightning-fast linting and formatting, replacing Prettier and ESLint.
- **Markdown Wiki Support**: Integration of the project's internal wiki into the TUI with semantic link parsing and focused scrolling.

### Changed

- Refactored `StatusBar` into a dynamic, data-driven organism.
- Migrated `Settings` and `Tasks` monitoring to the new React-based architecture.
- Optimized backend communication using typised Axios services.

### Fixed

- **Input Collisions**: Resolved issues where multiple UI components reacted to the same key presses.
- **Layout Corruption**: Fixed terminal rendering issues by moving to a Flexbox-based layout engine (Yoga).
- **Memory Leaks**: Resolved `MaxListenersExceededWarning` by optimizing input listener registration.

## [0.6.0] - 2026-01-25

### Added

- **FastAPI + HTMX GUI**: Migrated the web interface from Flask to FastAPI for better performance and async support.
- **HTMX Integration**: Smooth UI updates using partial templates and HTMX, reducing page reloads.
- **Real-time Logging**: Implemented Server-Sent Events (SSE) for live synchronization logs in the browser.
- **Theme Support**: Integrated Light and Dark mode using Bootstrap 5.3, with persistent state in the settings database.
- **Generic Settings UI**: A new settings page that dynamically renders and saves configuration options from the database.
- **Project Initialization**: New `project_init.py` to automate directory creation and database setup for new environments.
- **Sync Safety**: Added a global lock mechanism to prevent simultaneous build synchronizations.
- **Modern Tooling**: Switched from flake8 to Ruff for faster and more comprehensive linting and code quality.

### Changed

- Refactored `db_gui.py` to use a modular template structure in `Tools/templates/`.
- Enhanced `update_build_registry.py` to store detailed metadata like download status and sync timestamps.
- Updated `sync_wow_db.py` to automatically update the registry after successful build imports.

### Fixed

- Fixed UI nesting issues where entire pages were rendered inside themselves.
- Resolved database schema inconsistencies through automated migrations in `project_init.py`.

## [0.5.0] - 2026-01-25

### Added

- **Build Registry**: New `Build_Registry.db` to track all available WoW builds via Wago.tools API.
- **Settings Management**: `Settings.db` and `update_settings.py` for global configuration (e.g., thread workers).
- **Parallel Processing**: Multi-threaded table downloads and imports in `sync_wow_db.py`.
- **Intelligent Mapping**: Global column-to-table learning in `map_references.py`.
- **Build Heritage**: Automatic import of reference mappings from previous builds.
- **Enhanced UX**: Added `0a` (skip all) option in interactive mapping sessions.
- **Database Optimization**: Enabled WAL-mode and optimized PRAGMAs for faster SQLite operations.

### Changed

- Refactored `compare_builds.py` to use the new build registry and support automated missing build downloads.
- Improved `sync_wow_db.py` with robust delimiter detection (Comma/Semicolon) and better error handling.
- Cleaned up `map_references.py` code structure and removed redundant logic.
- Enhanced `find_val.py` to support cross-build searching and build-specific filtering via the `-build=` argument.

### Fixed

- Fixed CSV header corruption where multiple columns were merged due to incorrect delimiter detection.
- Resolved issues with incomplete build imports by adding API fallbacks.

## [0.4.0] - 2026-01-25

### Added

- Interactive reference mapping tool.
- Support for build-specific user mappings to prevent cross-version contamination.
- Fuzzy matching for table suggestions.

### Fixed

- Handling of corrupted column names in DB2 exports.
