# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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