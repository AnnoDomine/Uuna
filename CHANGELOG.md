# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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