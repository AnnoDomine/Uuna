# Grand Library - WoW Datamine Toolkit (V1.0.0-rc)

Welcome to the **Grand Library**, a high-performance, AI-orchestrated research platform for World of Warcraft data analysis. This toolkit transforms raw database files (DB2) from Classic to Midnight into semantically meaningful game intelligence using a multi-agent "Relay-Race" system.

📖 **[Visit the Internal Wiki](docs/wiki/Home.md)** - Comprehensive documentation on roles, architecture, and guides.

---

## 🏛️ How the System Works (The Relay Race)

The Grand Library utilizes a **Hub-and-Spoke Orchestration** model. No agent works in isolation; instead, they pass a "torch" (Event ID) along a chain of specialists.

1. **Librarian**: Receives the user query and spawns a **Task ID**.
2. **Courier**: The central heart. It decides the "path" and creates **Event IDs** for specialists.
3. **Specialists**:
   - **Archivist**: Mines the DuckDB Master for technical relations.
   - **Expedition Group**: Researches lore context from Wikis and Wowhead.
   - **Cartographer**: Visualizes findings as Mermaid ER-diagrams.
4. **Sentinel**: Automatically injected between research and delivery to ensure data sanitization and SQL security.
5. **Sages**: The final gatekeepers. They logically validate facts before granting an `APPROVE` verdict.

---

## ⚙️ The Scoring System (Blind Wisdom)

To ensure absolute integrity and prevent AI agents from "gaming the system," we utilize a **Blind Scoring** mechanism:

- **The Tinker**: Analyzes task complexity and sets a `max_potential` score directly in the database.
- **Specialist Agents**: Perform their work without knowing the points available.
- **The Observer**: Blindly loads the potential from the DB and awards a `quality_score`.
- **Isolation**: Agents only receive a **Success Percentage** (e.g., 95%). Absolute points remain hidden within the validation layer (Tinker/Observer).

---

## 💻 Technical Architecture

- **WoW_Master.duckdb**: Centralized columnar database utilizing MD5 row-level deduplication across 1500+ game builds.
- **role_memory.duckdb**: Dedicated long-term memory utilizing **DuckDB VSS** (Vector Similarity Search) for semantic pattern recognition.
- **AI Engine**: Local LLM orchestration via **Ollama** (Optimized for Qwen 3 8B).
- **API Gateway**: All database operations are proxied through a FastAPI middleware (`db_service.py`) to prevent concurrency locks.
- **Shared DB Pattern**: High-level tools utilize a centralized `db` instance (`shared_db_instance.py`) to streamline orchestration and prompt clarity.
- **Task Inspector**: Real-time TUI monitoring of the multi-agent relay race, providing granular visibility into events, agent reasoning, and scoring.
- **Command-Driven UI**: Vim-style CommandLine (`:goto`, `:settings`, `:mod`) for high-speed expert interaction.

---

## 🚀 Getting Started

### 1. Installation

The easiest way to get started is using the automated initialization script:

```bash
# Clone the repository
git clone https://github.com/AnnoDomine/Uuna.git
cd Uuna

# Run the automated setup
bash init.sh
```

The script will check for prerequisites (uv, Node.js, Ollama), set up the environment, initialize the database, and run hardware optimization.

### 2. Management & Development

The project includes a `manage.py` utility to centralize common tasks:

```bash
# Initialize the environment (Folders & DBs)
uv run manage.py init

# Analyze hardware and configure AI settings
uv run manage.py optimize

# Start the Database Service (API Gateway)
uv run manage.py serve

# Run the Master Ingester (Syncs DB2 to DuckDB)
uv run manage.py ingest --limit 50

# Run all stability tests
uv run manage.py test

# Autonomous research run
uv run python Tools/agents/ai_researcher_agent.py --start 11.1.0.59000 --limit 10
```

---

## 🤝 Contributing

We welcome contributions! Please read our **[Contributing Guide](docs/CONTRIBUTING.md)** to learn about our development process, coding standards, and how to get started.

---

## 🌍 Dynamic Localisation

The Grand Library is language-agnostic. By changing the `localisation` setting in the DuckDB registry, the Librarian will communicate in your preferred language (German, English, Japanese, etc.) while the internal technical logic remains precise in English.

---

_Created with ❤️ for the WoW Datamining Community._
