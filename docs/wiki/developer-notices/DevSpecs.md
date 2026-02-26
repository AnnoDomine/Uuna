# 🛠️ Developer Notices: Environment Specs

[⬅️ Back to Home](../Home.md)

This page lists the hardware and software specifications of the machine(s) used to develop, test, train, and run the Grand WoW Library AI agents.

## 🖥️ Primary Workstation Specs

These specifications represent the baseline environment where the current system is engineered and the massive data integration (DuckDB) is performed.

- **CPU**: AMD Ryzen 9 7900 (12-Core, 24-Thread High-End Processor)
- **GPU**: NVIDIA GeForce RTX 4070 Ti (12 GB VRAM - High-Performance AI Inference)
- **RAM**: 32 GB DDR5 (Current utilization ~11 GB active, 19 GB available for caching)
- **Storage**: 1 TB NVMe SSD (Primary Archive) + **External USB Storage** (used for long-term cold storage of legacy SQLite backups to save local NVMe space).
- **OS**: Linux (Ubuntu/Debian based)
- **AI Acceleration**: Local LLM execution via Ollama (optimized for CPU/GPU hybrid inference)

## 🧪 Testing & Training Notes

- **Database Performance**: DuckDB handles the 23GB+ archive with sub-second response times on this hardware.
- **Ingestion Speed**: The system processes approximately 2-3 full WoW builds per minute (including deduplication and indexing) on this multi-threaded setup.
- **AI Training**: Experimental "Dry Runs" and prompt engineering are calibrated to run efficiently on 7B to 14B parameter models (e.g., Qwen 2.5).

## 🛡️ Strict Quality & Reliability Standards

To maintain the professional integrity of the Grand Library, the following standards are enforced:

- **100% Type Safety**: No `any` types allowed. Every data structure is strictly defined.
- **Zero Warning Policy**: The project codebase is warning-free. All tools (Ruff, Biome, Pytest, Vitest) are configured to treat warnings as fatal errors.
- **Stability Runs**: CI/CD requires every PR to pass the entire test suite **3 times consecutively** to eliminate flaky tests and race conditions.
- **Conventional Integrity**: A strict conventional commit policy combined with a "No Force-Push" rule ensures a clean and traceable audit trail.
