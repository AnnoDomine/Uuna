# AGENT.md - WoW Datamine Toolkit Context

Always use Context7 MCP when I need library/API documentation, code generation, setup or configuration steps without me having to explicitly ask.

This document serves as the technical context for AI agents and developers. The project is a universal toolkit for World of Warcraft datamining, utilizing a multi-agent orchestration system. **Currently in Version 1.1.0-rc (Release Candidate).**

## Communication & Naming

- **User Interaction**: Communication with the human user is performed in **German**.
- **Naming Conventions**: All folder names, file names, variables, functions, classes, and methods must be in **American English**.
- **Data Content**: All data and internal documentation are in **American English**.

## Project Objectives

- **Focus**: Analysis of WoW Retail data (build history from Classic to Midnight).
- **Purpose**: Extraction, search, and linkage of DB2 data, Spells, Quests, and Dialogues.
- **Strategy**: Centralization of all WoW data in a highly optimized **DuckDB Master Archive** with system-wide row-level deduplication.

## Core Mandates & Security

- **Python Execution**: Python scripts MUST be executed exclusively using **uv** and Python **3.12**: `uv run python path/to/script.py`.
- **Package Management**: **uv** is the mandatory package manager. Use `uv add <package>` for new dependencies and `uv sync` to align the environment.
- **Addon Code**: The `addons/` directory is strictly **off-limits** for AI agents. Changes are only allowed upon explicit instruction.
- **Master Archive**: Local build-specific SQLite files are legacy. All data resides in the `archive` schema within `Data/WoW_Master.duckdb`.
- **Data Access**: Full access to DuckDB (schemas: `archive`, `registry`, `research`) and JSON maps in `Data/`.
- **AI Optimization**: Hardware-specific settings (`num_thread`, `num_ctx`, `num_gpu`) are stored in `Data/settings.json` and managed via the `ConfigManager`. This centralized configuration supports real-time updates and strict Pydantic validation.

## Project Structure (Modular)

- **Tools/core/**: Central services, DB initialization, API middleware, and registry management.
- **Tools/ingestion/**: Data acquisition (Wago.tools) and integration into the DuckDB Master.
- **Tools/migration/**: Legacy tools for migrating old SQLite datasets.
- **Tools/toolsets/**: Role-based toolsets and specialized tools (Atomic design).
- **Tools/agents/**: AI agent implementations and orchestration logic.
- **Tools/analysis/**: Statistical features, mapping tools, and diagram generation.
- **Tools/web/**: Modern Electron Desktop UI (`react-node/`) and legacy TUI components (`tui-node/`).
- **Tools/tests/**: Pytest suite for all tools and core logic.
- **Data/**: Central data storage (DuckDB, settings.json, Logs, temporary CSVs).

## Development Conventions & Guidelines

1. **No Redundancy**: Consistently avoid redundant code through modularization.
2. **Class-First Design**: Use Pydantic models for all structured data, including configuration and AI response templates. Models serve as the single source of truth for both validation and UI auto-completion.
3. **Outsourcing**: Prompts and SQL queries are strictly outsourced to dedicated files and folders within the tool directories (e.g., `Tools/toolsets/tools/.../queries/`).
3. **Secure API Protocol**: Agents NEVER execute raw SQL directly. They interact with the library via a restricted Middleware API (`db_service.py`) using dedicated `DBClient` and `AIClient`.
4. **Shared DB Instance**: Tools MUST NOT accept `db_client` as a parameter. Instead, they MUST import and use the global `db` instance from `Tools.core.shared_db_instance.py` to ensure consistent connectivity and cleaner orchestration prompts.
5. **Docstring Standard (Parser-Ready)**: All tool functions MUST follow the standardized docstring format for automated KI-parsing:
   - Line 1: Concise summary.
   - Args section: Parameters listed as `- name: description`.
6. **Test-Driven**: No class, method, or function is considered integrated without a passing test. A pre-filled test database is created if necessary.
7. **Full Code Delivery**: Always deliver the **complete code** for requests or changes, never fragments or partial edits.
8. **Documentation First**: Everything is documented cleanly in English. The Wiki (`docs/wiki/`) is the primary "User Manual" and must be kept up-to-date.
9. **Gamification**: Documentation utilizes RPG-style imagery (in `docs/wiki/images/`) to reflect the project's WoW theme.
10. **Safe Updates**: Avoid `write_file` for updating existing documentation or large files. Use the `replace` tool for surgical edits to preserve historical data.
11. **CLI-First**: All core functions must be primarily operable via the terminal. Interaction is driven by a central **CommandLine** interface.
12. **Unified Log Schema**: Format: `[{run_info} - {timestamp} - {level} - {process} - {build}]: {message}`.
13. **Strict Quality Policies**:
    - **No `any` Typed Policy**: The use of `any` is strictly prohibited in TypeScript and Python (use `object`, `unknown` or specific generics instead).
    - **Zero Warning Policy**: Code MUST NOT produce any warnings in `pytest`, `vitest`, `ruff`, or `biome`. All warnings are treated as errors.
    - **No-Force-Push Policy**: `git push --force` or `git push --force-with-lease` are strictly forbidden on shared branches (`main`, `master`, `dev`, `stage`). Rebase and merge conflicts MUST be resolved locally.

## Frontend Guidelines (Desktop / Electron / React)

The Desktop User Interface (DUI) follows a strict Enterprise frontend architecture based on **Electron**, **React**, **TypeScript**, and **Redux Toolkit**.

### 1. Interaction Model (Hybrid)

The UI combines a modern web interface with desktop capabilities.
- **Communication**: Interacts with the Python backend via the **Grand Library API** (FastAPI).
- **Auto-Completion**: Dynamic suggestions generated from backend Pydantic classes and Redux state.
- **Legacy TUI**: The former React (Ink) based Terminal User Interface is no longer maintained and remains for documentation purposes only.

### 2. Architecture (Atomic Design)

Components are divided into `Atoms`, `Molecules`, `Organisms`, and `Pages`. Each component resides in its own directory with the following schema:

- `ComponentName.tsx` (UI / Render Logic)
- `component_name.hooks.ts` (Business Logic / State / API Hooks)
- `component_name.types.ts` (Interfaces & Types)
- `component_name.constants.ts` (Static Data)
- `component_name.helpers.ts` (Pure Functions)
- `component_name.enums.ts` (Enums)

### 3. State Management

- **Local**: Primitives use `useState`. Complex structures (objects/arrays) ALWAYS use `useImmer` for safe, mutable updates via `draft`.
- **Global**: **Redux Toolkit** (RTK) manages app-wide data.
- **API Cache**: **RTK Query** is used for efficient data fetching and caching from the Grand Library API.

### 4. UI Library

- **MUI (Material UI) / Joy UI**: Modern, accessible component library for a polished desktop experience.
- **Icons**: Material Icons for consistent visual language.

### 5. Quality & Tooling

- **Linter/Formatter**: **Biome** is the mandatory tool for formatting and linting.
- **Node.js**: **Node.js 24** is the mandatory runtime version.
- **Package Management**: **pnpm** is the mandatory package manager. Use `pnpm add <package>` for new dependencies.
- **TypeScript**: Strict typing is required. Avoid `any` (except in `global.types.ts`).
- **No Shortcuts**: `@ts-ignore` or `@ts-nocheck` are strictly prohibited. Fix errors via correct typing or type guards.
- **ESM**: The project uses ECMAScript Modules. Relative imports must include the `.js` extension where applicable.

## The Library System (Orchestration)

A Hub-and-Spoke system for processing research tasks:

### Roles

1. **📚 The Librarian (Interface)**: Primary contact for the user. Synthesizes knowledge and manages the "memory" (`research.discoveries`). Validates data availability via `check_build_status`.
2. **🏃‍♂️ The Courier (Orchestrator)**: The heart of the system. Routes tasks via `task_id` between experts, manages the queue, and makes routing decisions.
3. **🏛️ The Archivist (DB Expert)**: Exclusive access to the DuckDB Master for finding relations and row IDs.
4. **🗺️ The Expedition Group (Research)**: Performs online research (Wago, Wowhead) to provide lore context.
5. **🛡️ The Sentinel (Middleware)**: Cleans data (sanitization) and verifies SQL statement security.
6. **🧙‍♂️ The Sages (Gatekeeper)**: Validate gathered information for logic; approve or send the Courier back for more research.
7. **🎨 The Cartographer (Visualizer)**: Generates Mermaid ER-diagrams to visualize data relationships.
8. **⚙️ The Tinker (Quantity)**: Assigns potential scores to tasks based on complexity, providing a baseline for quality assessment.
9. **👁️ The Observer (QA)**: The "Executioner". Mercilessly judges accuracy, formatting, and logic based on the Tinker's baseline and agent confidence.

## Data Model & Analysis

- **Unified Master Archive**: Uses MD5 row-hashing for cross-build deduplication.
- **Storage Strategy**: Local NVMe storage is optimized for the DuckDB Master. Legacy backups (SQLite zips) are moved to **External Cold Storage** and are not locally available.
- **Registry**: `registry.builds` manages the download and indexing status of all WoW versions.
- **Research DB**: Schema `research` in the Master DB stores tasks, events, statistical features, and discoveries.
- **Vector-Memory**: Long-term memory and embeddings are stored in a dedicated vector-enabled DuckDB (`Data/knowledge/`), utilizing DuckDB VSS for semantic retrieval of lore and data patterns.
- **Task-ID Lifecycle**: Every request receives a UUID that persists through all roles to ensure a complete audit trail.

## Tooling System

- **Atomization**: Tools used by agents are atomized. Each tool has its own file, SQL query, and test. Nothing is integrated without a passing test.
- **Specification**: Tools are granted specifically at the agent level. Agents have access to their role-specific toolset (e.g., `archivist_tool_set.py`) and the `global_tool_set.py`.
- **Classification**: Every agent has a separately defined "Skill-Set" document (`docs/wiki/roles/`) containing in-depth procedural instructions ("How-to").
- **Prompting Structure**: Prompts must always start with the identity header:

```txt
ROLE: You are the {AGENT_ROLE}. A {short_description}.
CONTEXT:
Detailed procedures regarding your identity and workflow are located in your Skill-Set at {PATH_TO_ROLE_MD}.
Tools required for your task are found in the (global-tool-set) and ({agent}-tool-set).
---
{Specific task instructions continue here...}
```

- **Admin Tools**: Tools marked as `ADMIN_TOOLS` (e.g., `compare_builds`, `run_mass_indexing`) are reserved for human administrators and MUST NEVER be accessible by AI agents to prevent data corruption.

# Logging

Milestones are documented in `CHANGELOG.md` and `HISTORY.md`.

## 🛠️ AI PATCH: Common Pitfalls & Verified Solutions

### 1. Process Management (Background Tasks)

- **Problem**: Standard `nohup` or `&` often fail to keep processes alive.
- **Solution**: Use an inline Python call with `subprocess.Popen` and `start_new_session=True`.
- **Snippet**: `.venv/bin/python3 -c "import subprocess, os; subprocess.Popen(['.venv/bin/python3', '-u', 'path/to/script.py'], stdout=open('log.txt', 'a'), stderr=subprocess.STDOUT, start_new_session=True)"`

### 2. SQL & DuckDB Implementation

- **F-String Escaping**: Double curly braces `{{` and `}}` are mandatory when templates contain literal braces.
- **Dynamic Identifiers**: Table names cannot be parameter-bound. Always sanitize and use double quotes (e.g., `archive."{table_name}"`).
- **Sequences**: Use `DEFAULT nextval('seq_name')` for auto-incrementing IDs.

### 3. Shell Command Quoting

- **Problem**: Nested quoting errors in complex one-liners.
- **Solution**: Maintain a strict hierarchy of single (`'`) and double (`"`) quotes.

### 4. Robust JSON Parsing

- **Problem**: AI output often contains markdown wrappers or prefix text.
- **Solution**: Implement "robust decoding" to strip markdown and extract content between the first `{` and last `}`.
