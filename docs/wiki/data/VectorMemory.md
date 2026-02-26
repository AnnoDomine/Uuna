# 🧠 Long-Term Vector Memory

[⬅️ Back to Home](../Home.md)

Each role possesses an isolated "Memory Bank" to store long-term insights and patterns.

## Implementation

- **Technology**: DuckDB VSS (Vector Similarity Search).
- **Storage**: `Data/knowledge/role_memory.duckdb`.
- **Isolation**: The Archivist cannot read the Expedition Group's memory.

## Usage

When an agent starts a task, they query their own vector space for similar past assignments.

- **Example**: "I remember a similar table structure in Build 9.0.1; column 4 was usually a cooldown."

## Evolution

This memory is updated _after_ the **Sages** approve a result. Only "Approved Knowledge" is allowed to be committed to the long-term vector memory.
