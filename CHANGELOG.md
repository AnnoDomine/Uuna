# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
