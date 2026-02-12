# Grand Library - WoW Datamine Toolkit

Welcome to the **Grand Library**, a high-performance, AI-orchestrated research platform for World of Warcraft data analysis. This toolkit transforms raw database files (DB2) from Classic to Midnight into semantically meaningful game intelligence using a multi-agent "Relay-Race" system.

📖 **[Visit the Internal Wiki](docs/wiki/Home.md)** - Comprehensive documentation on roles, architecture, and guides.

---

## 🏛️ How the System Works (The Relay Race)

The Grand Library utilizes a **Hub-and-Spoke Orchestration** model. No agent works in isolation; instead, they pass a "torch" (Event ID) along a chain of specialists.

1.  **Librarian**: Receives the user query and spawns a **Task ID**.
2.  **Courier**: The central heart. It decides the "path" and creates **Event IDs** for specialists.
3.  **Specialists**:
    *   **Archivist**: Mines the DuckDB Master for technical relations.
    *   **Expedition Group**: Researches lore context from Wikis and Wowhead.
    *   **Cartographer**: Visualizes findings as Mermaid ER-diagrams.
4.  **Sentinel**: Automatically injected between research and delivery to ensure data sanitization and SQL security.
5.  **Sages**: The final gatekeepers. They logically validate facts before granting an `APPROVE` verdict.

---

## ⚙️ The Scoring System (Blind Wisdom)

To ensure absolute integrity and prevent AI agents from "gaming the system," we utilize a **Blind Scoring** mechanism:

*   **The Tinker**: Analyzes task complexity and sets a `max_potential` score directly in the database.
*   **Specialist Agents**: Perform their work without knowing the points available.
*   **The Observer**: Blindly loads the potential from the DB and awards a `quality_score`.
*   **Isolation**: Agents only receive a **Success Percentage** (e.g., 95%). Absolute points remain hidden within the validation layer (Tinker/Observer).

---

## 💻 Technical Architecture

*   **WoW_Master.duckdb**: Centralized columnar database utilizing MD5 row-level deduplication across 1500+ game builds.
*   **role_memory.duckdb**: Dedicated long-term memory utilizing **DuckDB VSS** (Vector Similarity Search) for semantic pattern recognition.
*   **AI Engine**: Local LLM orchestration via **Ollama** (Optimized for Qwen 3 8B).
*   **API Gateway**: All database operations are proxied through a FastAPI middleware (`db_service.py`) to prevent concurrency locks.

---

## 🚀 Getting Started

### 1. Installation
```bash
# Clone and setup environment
git clone https://github.com/AnnoDomine/Uuna.git
cd Uuna
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the DB Service
bash Tools/start_db_service.sh
```

### 2. Fetching Builds
```bash
# Update the registry from Wago.tools
.venv/bin/python3 Tools/ingestion/update_build_registry.py

# Start the Master Ingester (Syncs DB2 to DuckDB)
bash Tools/start_master_ingester.sh
```

### 3. Running Research
```bash
# Trigger an autonomous research run
.venv/bin/python3 Tools/agents/ai_researcher_agent.py --start 7.3.5.25600 --limit 10
```

---

## 🌍 Dynamic Localisation
The Grand Library is language-agnostic. By changing the `localisation` setting in the DuckDB registry, the Librarian will communicate in your preferred language (German, English, Japanese, etc.) while the internal technical logic remains precise in English.

---
*Created with ❤️ for the WoW Datamining Community.*
