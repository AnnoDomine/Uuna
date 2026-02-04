# 💻 System Requirements
[⬅️ Back to Home](../Home.md)

To run the Grand WoW Library and its AI agents effectively, your system should meet the following specifications.

## Hardware
*   **Storage**: 50GB+ (The Unified DuckDB Archive is highly compressed but stores millions of rows).
*   **RAM**: 16GB minimum (32GB recommended for large-scale indexing).
*   **CPU**: Multi-core processor (The Ingester and Indexer are multi-threaded).

## Software & Environment
*   **Operating System**: Linux (Ubuntu/Debian recommended) or macOS.
*   **Python**: Version 3.9 or higher.
*   **AI Backend**: [Ollama](https://ollama.ai/) (Required for local LLM execution).
*   **Database**: DuckDB (Handled automatically via Python).
*   **Memory Cache**: Redis (Optional, used for high-performance agent communication).
