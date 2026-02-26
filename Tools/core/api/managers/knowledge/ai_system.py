AI_CORE_CONCEPTS = [
    {
        "topic": "Large Language Models (LLMs)",
        "context": "The system uses local LLMs (Qwen 3) via Ollama. They are stateless but receive context via Retrieval-Augmented Generation (RAG) from the Vector DB.",
    },
    {
        "topic": "Vector Embeddings",
        "context": "Semantic memory uses 4096-dimensional vectors. Similarity is calculated via cosine distance in DuckDB VSS.",
    },
    {
        "topic": "Agent Autonomy",
        "context": "Agents are specialized workers with tool access. They follow the Hub-and-Spoke model orchestrated by the Courier.",
    },
    {
        "topic": "Agent Isolation",
        "context": "Agents are isolated. They have no direct access to knowledge of other agents. If an agent want to know something from another, the agent needs to request this knowledge.",
    },
]

SYSTEM_ARCHITECTURE = [
    {
        "component": "Task-ID Lifecycle",
        "context": "Every request has a UUID. All agents must pass this ID to maintain the 'Red Thread' of an investigation.",
    },
    {
        "component": "Event-ID Lifecycle",
        "context": "Every task have a group of different events. Every step an agent do, needs to be integrated by an event. When an agent is finished with the event, it havbe to send the event ID beside the task ID.",
    },
    {
        "component": "A2A Middleware",
        "context": "Agent-to-Agent communication is strictly handled via the Library API to ensure logging and security.",
    },
]

SCORING_AND_QUALITY = [
    {
        "mechanism": "The Observer (The Only Judge)",
        "context": "The Observer is the EXCLUSIVE authority for assigning scores. It monitors all actions and penalizes hallucinations or errors (Bad Boy Principle).",
    },
    {
        "mechanism": "Special Scoring Paths",
        "context": "The Librarian, Tinker, and Observer roles have unique, specialized scoring mechanisms distinct from standard agents.",
    },
    {
        "mechanism": "60/40 Evaluation",
        "context": "The system reliability is weighted: 60% automated verification (Observer) and 40% logical consistency check (Sages).",
    },
    {
        "mechanism": "The Sages (Gatekeepers)",
        "context": "Sages do NOT assign scores. They verify the logical coherence and 'lore-integrity' of results before approval.",
    },
]

MEMORY_SYSTEMS = [
    {
        "system": "Short-Term (Research DB)",
        "context": "SQLite/DuckDB storing live tasks, events, and raw logs of current operations.",
    },
    {
        "system": "Long-Term (Vector Memory)",
        "context": "The 'Approved Knowledge' store. Only data that passed the Sages' logic check is committed here.",
    },
]
