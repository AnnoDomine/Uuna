# WoW Datamine Toolkit (Retail 12.0 "Midnight")

Welcome to the **WoW Datamine Toolkit**, a high-performance, AI-enhanced platform specialized in extracting, analyzing, and decoding World of Warcraft data. Optimized for **Patch 12.0 (Midnight Prepatch)**, this toolkit bridges the gap between raw DB2 files and semantic game intelligence.

---

## 🚀 The Vision
This project has evolved from a simple data extractor into an **Autonomous Research Engine**. By leveraging local Large Language Models (LLMs), the toolkit doesn't just read data—it learns the architecture of Azeroth. It identifies new game systems (like the upcoming Housing features), maps complex database references, and preserves lore discoveries across thousands of game builds.

---

## 💻 System Requirements

To run the toolkit effectively, especially the AI components, the following hardware is recommended:

*   **Operating System**: Linux (Ubuntu/Debian recommended) or macOS.
*   **Python**: v3.10 or higher.
*   **Memory**: 16GB RAM minimum (32GB+ recommended for parallel AI tasks).
*   **GPU (Optional but Recommended)**: NVIDIA RTX 3060 or higher (8GB+ VRAM) for local AI acceleration.
*   **Storage**: SSD with at least 50GB free space (for SQLite databases and AI models).
*   **AI Engine**: [Ollama](https://ollama.com/) installed and running.

---

## 🛠️ Initialization

Follow these steps to set up your local research environment:

1.  **Clone & Environment**:
    ```bash
    git clone https://github.com/AnnoDomine/Uuna.git
    cd Uuna
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **System Init**:
    Initialize the directory structure and core settings:
    ```bash
    python3 Tools/project_init.py
    ```

3.  **Sync Registry**:
    Fetch the latest build list from Wago.tools:
    ```bash
    python3 Tools/update_build_registry.py
    ```

4.  **AI Setup**:
    Ensure Ollama is running and pull the required models:
    ```bash
    ollama pull qwen3:8b
    ollama pull qwen3-embedding
    ```

---

## 🕹️ Controlling the System

The toolkit is designed with a **CLI-First** philosophy, allowing for powerful automation.

### 1. Data Management
```bash
# Sync a specific build (Download CSV -> Convert to SQLite)
python3 Tools/sync_wow_db.py 12.0.0.65655

# Perform a mass-sync of all available historical builds
bash get_all_builds.sh
```

### 2. AI-Powered Research (The "Archivist")
The AI Agent analyzes statistical signatures to decode unknown columns:
```bash
# Configure AI parameters (Threads, Cooldown, Limits)
python3 Tools/ai_control.py set threads 6
python3 Tools/ai_control.py list

# Start an autonomous research session
python3 Tools/ai_researcher_agent.py --start 7.3.5.25600 --end 12.0.0.65655
```

### 3. Exploration & Comparison
```bash
# Global Search: Find any ID or Text across all tables
python3 Tools/find_val.py "Kun Lai"

# Compare Builds: See what Blizzard changed between versions
python3 Tools/compare_builds.py 12.0.0.65560 12.0.0.65655

# Web UI: Browse data with a modern FastAPI + HTMX interface
python3 Tools/db_gui.py
```
*Note: In the Web UI, use **Ctrl+K** to open the Command Palette for rapid navigation.*

---

## 🧪 Integrated Technologies

*   **Language**: Python 3 (Pandas, SQLite3, FastAPI).
*   **Frontend**: HTMX & Jinja2 (Zero-JS feel, real-time SSE streaming).
*   **Database**: SQLite (WAL-mode optimized for high concurrency).
*   **AI/ML**: Ollama API, Qwen 3 (8B) LLM, Vector Embeddings.
*   **Data Source**: Wago.tools API.

---

## ❤️ Acknowledgments

This project is a tribute to the passion of the World of Warcraft datamining community. 

Special thanks to:
*   **Wago.tools** for providing the essential data pipes.
*   The developers of **Ollama** and **Meta/Qwen** for making high-end AI accessible on local hardware.
*   Every explorer who ever looked at a `Field_xxx` and wondered, *"What does this do?"*

*Datamining is more than just looking at files; it's about preserving the history of a digital world. Thank you for being part of this journey.*

---
*Created with ❤️ by AnnoDomine & The Archivist Agent.*
