# Task Skill: Relationship Visualization

## Objective
To generate a syntactically correct and visually organized Mermaid ER-diagram from a list of confirmed database mappings.

## Procedural Steps
1.  **Ingest Mappings**: Read the list of confirmed table-to-table relationships (e.g., `TableA.ColX -> TableB`).
2.  **Define Entities**: Create an `erDiagram` block and list each involved table as a node.
3.  **Establish Links**: Draw relationships using Mermaid cardinality syntax:
    - `||--o{` (One-to-Many): The most common type for ID references.
    - `||--||` (One-to-One): For extension tables or primary key splits.
4.  **Labeling**: Use the column name as the label for the relationship line (e.g., `TableA ||--o{ TableB : "SpellID"`).
5.  **Grouping**: If multiple columns link the same two tables, combine them into a single line with a multi-label if necessary to reduce clutter.

## Constraints
- **Valid Names**: Ensure table names do not contain illegal characters for Mermaid (use quotes if necessary).
- **Size Limit**: Avoid including more than 20 tables in a single diagram unless explicitly requested.

## Output Requirements
Return a JSON object containing:
- `mermaid`: The raw string of the Mermaid `erDiagram`.
- `description`: A short summary of the mapped structure.
