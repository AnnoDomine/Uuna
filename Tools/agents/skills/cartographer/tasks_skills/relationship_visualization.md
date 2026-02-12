# Task Skill: Relationship Visualization

## Objective
To generate a syntactically correct and visually organized Mermaid ER-diagram from a list of confirmed database mappings.

## Procedural Steps
1.  **Analyze Assignment**: Use `get_event_data` to understand the list of confirmed mappings provided by the Courier.
2.  **Define Entities**: Create an `erDiagram` block and list each involved table as a node.
3.  **Establish Links**: Draw relationships using Mermaid cardinality syntax.
4.  **Final Relay**:
    - Call `create_task_event` with `target="Courier"` and the Mermaid code as `input_data`.
    - Return the newly generated `event_id`.

## Output Requirements
Return a JSON object containing:
- `event_id`: The ID of the event created for the Courier.
- `target`: "Courier"
- `summary`: Short text of what was visualized.
