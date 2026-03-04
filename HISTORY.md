# Project History - WoW Datamine Toolkit

## [1.1.0-rc] - 2026-03-03 - "The Desktop Evolution"

### Added
- **Electron Client**: Introduced the modern desktop client built with Electron, React, and Redux Toolkit, offering a richer UI and better desktop integration.
- **Grand Library API Enhancement**: Modularized the FastAPI backend and implemented automated DuckDB schema migrations based on Pydantic models.
- **Legacy TUI Migration**: Formally deprecated the terminal-based user interface (TUI) in favor of the more powerful and user-friendly desktop client.

## [1.0.0-rc] - 2026-02-26 - "The Release Candidate"

### Added
- **V1 Milestone reached**: The multi-agent orchestration system is now fully stable and verified through 94+ Python tests and 58+ TUI tests.
- **Midnight Pre-Release Support**: Added infrastructure to handle the upcoming Midnight expansion builds, including pre-release registry synchronization.
- **Unified Release Documentation**: Fully translated and updated history and changelog systems to reflect the transition from Alpha/Beta to Release Candidate.
- **Finalized Orchestration Protocol**: The "Relay-Race" system with 9 agents (Librarian, Courier, Archivist, Expedition Group, Sentinel, Sages, Cartographer, Tinker, Observer) is now functionally complete.

### Changed
- **Documentation Standard**: Moved all primary project history and changelogs to English to support international collaboration and standardized AI processing.
- **UX/UI Stabilization**: Refined the command-driven TUI to prevent layout shifting and improved focus management for high-speed research tasks.

### Fixed
- **Tuple Index Out of Range**: Resolved critical failures in `get_task_context` when retrieving tasks with complex build assignments.
- **UI State Corruption**: Fixed a "length of undefined" crash in the Build Selection hook by implementing robust initial state handling.
- **Linter Integrity**: Eliminated all remaining ruff and biome warnings to satisfy the "Zero Warning Policy" for the V1 release.

## [0.10.0-alpha] - 2026-02-21 - "The Command-Driven Evolution"

### Added
- **Vim-style CommandLine**: Radical redesign of the TUI. Static navigation was replaced by a central command line supporting commands like `:goto`, `:settings`, and `:mod`.
- **Dynamic Auto-Completion**: Implementation of `Ctrl+Tab` to navigate through commands and deeply nested configuration paths.
- **TUI Mod System**: Introduction of a modular extension interface. New tools can now be easily registered under the `:mod:` namespace.
- **Class-First Configuration**: Migration of all settings to `Data/settings.json`. A new `ConfigManager` uses Pydantic for runtime validation and provides the structure dynamically to the frontend.
- **Pydantic AI Orchestration**: All agent roles were switched to Pydantic-based schemas. This guarantees type-safe AI responses and improves process transparency through enforced reasoning (`reason`, `context`).
- **Global RAG Integration**: Automatic semantic search in long-term memory (Vector-DB) for every AI request. Results are filtered by quality (scoring) and injected as context.
- **AI Learning Phase**: The Observer now extracts "Lessons Learned" for the involved agents after each successful task and stores them with quality scores in the vector DB.
- **Isolated Pattern Training**: A new training system allows the AI to be trained in isolated loops (5 rounds, 3 attempts) on compliance with specific Pydantic patterns (controllable via `:mod:trainer`).

### Changed
- **SQL-Zero-Python Policy**: Complete elimination of hardcoded SQL strings from Python logic. All queries are now loaded from the `queries/` directory.
- **Hardened Security**: Integration of SQL injection protection and prompt sanitization as standard in all core components.

### Fixed
- **TUI Focus Conflicts**: Resolution of key overlaps through a revised `EFocusAreal` system that prioritizes the CommandLine.

## [0.9.15] - 2026-02-19 - "Clean Architecture & Industrial Testing"

### Added
- **Expedition Group Toolset**: Full implementation of the toolset for online lore research (Wiki, Wago, web content) with automatic caching logic.
- **Observer Toolset Upgrade**: Integration of consistency checking tools (`check_logical_consistency`) and final verdict mechanisms for the Observer.
- **Comprehensive Backend Test Suite**: Implementation and stabilization of 68 unit tests for all agent tools using `pytest` and `unittest.mock`.
- **Atomic Task Validation**: Every tool was validated and adjusted against the AI parsing standards defined in `AGENT.md`.

### Changed
- **Parser-Ready Docstrings**: Complete refactoring of all tool docstrings to the standardized "Short summary + Args list" format for error-free AI orchestration.
- **Shared DB Architecture**: Conversion of complex analysis workflows (Reference Mapping, Build Comparison) to the global `db` instance pattern to reduce prompt complexity.
- **Codebase Cleanup**: Removal of all redundant `sys.path` hacks and module resolution workarounds in favor of clean `PYTHONPATH` control via `manage.py`.

### Fixed
- **Stable Mocks**: Resolution of race conditions and incorrect SQL detection in test mocks for `compare_builds` and `map_column_references_workflow`.
- **Import Integrity**: Correction of missing dependencies in analysis tools (e.g., `save_discovery` in `perform_column_discovery`).

## [0.9.14] - 2026-02-18 - "Automated Setup & Hardware Synergy"

### Added
- **One-Click Setup (`init.sh`)**: A new interactive bash script that checks, installs, and configures the entire development environment (uv, Node.js, pnpm, Ollama, models).
- **Hardware Analyzer & Auto-Config**: Introduction of the `optimize` command in `manage.py`. The system now analyzes CPU, RAM, and GPU (NVIDIA, AMD, Apple Silicon) and suggests optimal settings.
- **Three Acceleration Modes**: Explicit support for `CPU`, `GPU`, and `Hybrid` (Both) modes for optimal use of system resources.
- **Comprehensive TUI Test Suite**: Implementation of unit tests for all organisms, molecules, and hooks of the TUI using Vitest and `ink-testing-library`.

### Changed
- **Atomic Design Finalization**: Completion of the TUI refactoring. All business logic was moved from components to hooks to ensure 100% testability.
- **Dynamic AI Client**: The `AIClient` now loads its configuration dynamically from the DuckDB (`registry.settings`) and uses a caching system for performance optimization.
- **Documentation Upgrade**: Updated `Requirements.md` and `CONTRIBUTING.md` with a focus on model setup (Qwen 3 8B) and hardware requirements.

## [0.9.13] - 2026-02-14 - "The Inspector & Global Connectivity"

### Added
- **Interactive Task Inspector**: Implementation of a 3-column view for monitoring research tasks. Users can now select tasks, view their event chain, and track detailed results including scoring in real-time.
- **Centralized DB Architecture**: Introduction of `shared_db_instance.py`. All tools now access a global database object, which slims down the codebase and removes technical parameters from AI prompts.
- **Atomic UI Refactoring**: Full modularization of the tasks page into `TaskList`, `EventList`, and `TaskDetails` organisms according to the Atomic Design standard.
- **Threadpool Integration**: Transition of the AI router to asynchronous threadpool execution to ensure TUI responsiveness (health checks) during complex AI requests.

### Changed
- **Parser-Ready Tools**: Revision of over 40 tool functions. All docstrings now follow a strict schema allowing automated extraction of parameters and descriptions for the AI.
- **Unified Focus Management**: Integration of the `useScopedInput` hook into the start page (`Home.tsx`) to avoid control conflicts.

### Fixed
- **Frontend-Backend Sync**: Correction of 404 errors and connection drops through port harmonization and improved exception handling.
- **DuckDB Concurrency**: Resolution of file locks through consistent use of the middleware API.

## [0.9.11] - 2026-02-12 - "The Relay-Race & Blind Wisdom"

### Added
- **Atomized Skill Sets**: Introduction of Markdown-based "training" for all 9 agents. Every agent now knows exactly which procedural steps are necessary for their tasks via `get_my_skills`.
- **Event Relay Logic**: The system was switched from volatile function calls to a seamless chain of Event IDs ("torch race"). This guarantees 100% auditability of every decision.
- **Vector Memory (RAG)**: Integration of DuckDB VSS as long-term memory. Agents can now semantically search for patterns in previous research tasks.
- **Internationalization**: Dynamic localization of user communication. The Librarian now speaks several languages (tested: German, English, Japanese) based on system settings.
- **Blind Scoring**: Full isolation of the evaluation level. Agents and the Courier have no access to absolute scores (Max Potential), preventing system manipulation.

### Changed
- **Role Consolidation**: Merging of "Data Engineer" into the Archivist and "Senior Critic" into the Sages for a leaner 9-agent model.
- **Surgical Prompting**: Transition of all AI instructions to local tool prompts with references to the new skill files.

### Fixed
- **Wiki Scraping**: Resolution of 403 errors when accessing Warcraft Wiki through referer header injection.
- **Integrity**: Elimination of redundancies in the tool hierarchy (global vs. agent-specific).

## [0.9.10] - 2026-02-11 - "The API Gateway & Parallel Ingestion"

### Added
- **API-First Architecture**: Introduction of `db_service.py` as a central FastAPI gateway. All read and write access to the DuckDB master now occurs via a decoupled interface.
- **Central DB Client**: Implementation of the `DBClient` class in `Tools/core/db_client.py`. This enables all Python tools uniform, thread-safe access without direct file locks.
- **Multi-Worker Ingestion**: `master_ingester.py` now supports parallel table downloads and imports using `ThreadPoolExecutor`.
- **Isolated Workspaces**: Use of unique temporary tables (`tmp_table_build_version`) per worker to prevent collisions during parallel write operations.
- **Robust Data Pipeline**: Expansion of CSV parsing with `ignore_errors=True` and `null_padding=True` to catch structural errors in remote data (e.g., `NeighborhoodPlot`).
- **Background Resilience**: Upgrade of start scripts to a Python-based process decoupling (`start_new_session=True`) that runs stably independent of the terminal.

### Changed
- **Decoupling**: Conversion of `feature_extractor.py` and `master_ingester.py` to API access via `DBClient`.
- **Module Resolution**: Optimization of `PYTHONPATH` handling to make the `Tools` package available system-wide.

### Fixed
- **Schema Evolution Race Conditions**: Case-insensitive column checking prevents crashes with different capitalization in new builds.
- **API Debugging**: Integration of traceback printing in the `/execute` endpoint for fast error analysis in `api.log`.

## [0.9.9] - 2026-02-08 - "The Responsive Layout & Semantic Memory"

### Added
- **Dynamic Full-Screen TUI**: Introduction of the `useTerminalDimensions` hook. The interface now scales without delay with every size change of the terminal window.
- **Enterprise Layout Stability**: Transition to a "Fixed-Fluid" architecture. Every UI element now has strictly defined dimensions (static or percentage), eliminating layout jumps and shifts.
- **Vector Memory Explorer**:
  - Functional semantic search in agent memory.
  - Two-column layout with real-time filtering by roles (Librarian, Archivist, etc.).
  - Display of match quality (similarity score) and metadata origin.
- **Scoring Board Optimization**: Redesign of the overview into a side-by-side model (agent stats vs. scoring history) for better readability on wide terminals.
- **Interactive Wiki & Help**:
  - **Wiki**: Markdown content is now focusable and scrollable.
  - **Help**: New static page for CLI interaction help with keybinding table.
- **Python Backend Synchronization**: Adjustment of the `VectorManager` to the frontend (id, role, score fields) for seamless data flows.

### Changed
- **Structure**: Separation of "Help" logic from "Wiki" documentation.
- **Components**: `ScrollableSelection` and `ScrollArea` were optimized for maximum flexibility within container layouts.

### Fixed
- **Scroll-In-View**: Focused list elements are now reliably pushed into the visible area.
- **Type Safety**: Final elimination of all `@ts-ignore` legacy burdens through correct API interface definitions.

## [0.9.8] - 2026-02-08 - "The React TUI & Enterprise Standards"

### Added
- **Node.js/Ink Migration**: Radical technology change of the user interface from Python Textual to **React (Ink)**. This enables true Flexbox layout and a more stable render engine (Yoga).
- **Enterprise-Standard Architecture**: Introduction of a strict frontend pattern:
  - **Atomic Design**: Hierarchical separation into Atoms, Molecules, Organisms, and Pages.
  - **Logic Decoupling**: Consistent use of custom hooks (`.hooks.ts`) to separate business logic and UI.
  - **Type Safety**: Full TypeScript integration without compromises (strict `@ts-ignore` block).
- **Global State & Immutability**: Use of **Zustand** for app-wide state management and **Immer** for safe, mutable state updates via `draft`.
- **Scoped Focus System**: Development of the `useScopedInput` hook for exclusive control of UI areas. Prevents key collisions between sidebar and content.
- **Backend Orchestration**: Fully automated management of the Python backend (FastAPI/Uvicorn):
  - **Auto-Start**: TUI starts the backend independently if needed.
  - **Health Checks**: Periodic checking of API availability.
  - **Clean Exit**: Automatic termination of all background processes when closing the TUI.
- **Local Patching Framework**: New `Patches/` system for integrating and repairing external Ink addons (e.g., switching from CommonJS to ESM for `ink-markdown`).
- **Virtualized Content Scrolling**: Implementation of `ScrollArea` and `ControlledScrollView` for fluid navigation in large lists and documentations.
- **Biome Integration**: Introduction of **Biome** as an ultra-fast replacement for ESLint and Prettier (format & lint on save).

### Changed
- **Navigation Flow**: Transition to a state-controlled switch pattern for lightning-fast page changes.
- **StatusBar Revamp**: Conversion to a dynamic, data-driven organism with real-time indicators.
- **Settings & Tasks Integration**: Transfer of central mining functions to the new React architecture.

### Fixed
- **Terminal Rendering Bugs**: Resolution of layout shifts and corrupt character cells by switching to React components.
- **MaxListeners Warnings**: Optimization of keyboard listener management to avoid memory leaks.

## [0.9.5] - 2026-02-01 - "The Library Orchestration & Scoring Logic"

### Added
- **Library Multi-Agent Architecture**: Introduction of a specialized orchestration system with clearly defined roles:
  - **Librarian**: Central user interface and knowledge synthesis.
  - **Courier**: Heart of the orchestration, manages task routing and queue prioritization.
  - **Archivist**: Expert for the DuckDB master and data relations.
  - **Expedition Group**: Specialist for online lore research (Wowhead, Wago).
  - **Sentinel**: Middleware for data sanitization and SQL security.
  - **Sages**: Final instance for knowledge verification (gatekeeper).
- **Advanced Scoring Framework**: Introduction of highly efficient reinforcement logic for AI quality assurance:
  - **The Tinker**: Quantitatively evaluates "work difficulty" (Max Potential) without context bias.
  - **The Observer**: Strict qualitative evaluation (Actual Score) incl. honesty check (comparison with agent confidence).
  - **Cooperated Learning**: Final scoring based on team synergy (60% CPP) and process efficiency (40% Task Score).
- **Human-in-the-Loop Training**: Implementation of `AI_PHASE_TRAINING` for calibrating the "judges" using fictitious scenarios and manual user feedback.
- **Master Ingester Pipeline**: New highly efficient tool for direct import from Wago.tools into DuckDB:
  - **MD5 Content Deduplication**: Identical data sets across 1500+ builds are physically stored only once.
  - **Unified Build Data Map**: Central linking of builds to deduplicated content hashes.
- **Systematic Project Wiki**: Establishment of an RPG-themed user manual in `docs/wiki/` (English First) with:
  - Detailed role descriptions and architecture diagrams.
  - SVG-based agent portraits for gamification.
  - Installation and ingestion guides.
- **AI PATCH System**: Establishment of a best-practice catalog in `AGENT.md` to avoid technical pitfalls (process management, SQL injection, JSON parsing).

### Changed
- **Tools Reorganization**: Full modularization of the `Tools/` directory into `core`, `ingestion`, `analysis`, `agents`, `web`, and `tests`.
- **Log Standardization**: Introduction of a uniform, highly informative log schema for all system components.
- **SQL Outsourcing**: Consistent separation of logic and data by externalizing all SQL queries into the `queries/` directory.
- **Storage Optimization**: Outsourcing of legacy backups (SQLite) to external cold storage; optimization of local SSD for the DuckDB master.

### Fixed
- **Stability Breakthrough**: Resolution of "Missing Table" warnings through direct CSV stream import from Wago.tools.
- **Background Process Resilience**: Solution for terminal session drops through decoupled Python sessions (`start_new_session=True`).
- **DuckDB Constraint Fix**: Correction of auto-increment syntax for sequences and primary keys.

---

## [0.9.0] - 2026-02-01 - "The Master Archive & DuckDB Integration"

### Added
- **DuckDB Master Integration**: Transition of the central storage to **DuckDB** (`WoW_Master.duckdb`) for handling hundreds of millions of records with minimal storage requirements.
- **Unified Middleware (`db_service.py`)**: Implementation of an asynchronous FastAPI service for orchestrating master DB access for all AI agents and tools.
- **Mass Migration & Archiving**: New highly efficient tool `migrate_to_master.py` with:
  - **6-Core Parallelization**: Simultaneous migration of 6 builds via DuckDB workers.
  - **Auto-Archiving**: Automatic zipping and moving of integrated SQLite files to `Data/backups/archived_sqlite/`.
  - **Heuristic Filtering**: Intelligent detection of incomplete builds to avoid corrupt archive data.
- **Uuna-Rule QA Framework**: Mandating an automated test run (`run_qa_test.sh`) before any major change to ensure mapping integrity.
- **Persistent Knowledge Migration**: Successful transfer of legacy knowledge (mappings, discoveries) to the new master schema.

### Changed
- **Performance Boost**: Reduction of mapping validation times through DuckDB indexing and asynchronous ID checking.
- `ai_researcher_agent.py`: Agent now uses the middleware API instead of direct SQLite connections for improved resilience.
- **Logging Standardization**: All logs are now centrally captured and structured in `Data/logs/`.

### Fixed
- Resolution of DuckDB startup problems through correction of incorrect PRAGMA commands and transition to thread-safe connections.
- Stabilization of parallel write access by removing blocking global locks in favor of native DuckDB concurrency.
