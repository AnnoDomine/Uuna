# Task Skill: Online Lore Research

## Objective
To find and extract relevant historical and gameplay context for specific WoW entities (NPCs, Spells, Quests, Items) from trusted external wikis.

## Procedural Steps
1.  **Analyze Assignment**: Use `get_event_data` to understand the research objective assigned by the Courier.
2.  **Search Strategy**: Use the `search_wow_wiki` tool with specific keywords (e.g., "Quest: The Missing Diplomat").
3.  **Content Retrieval**: Fetch the top 1-2 search results using the `fetch_web_content` tool.
4.  **Relay to Sentinel**: 
    - Compile findings into a structured dictionary.
    - Call `create_task_event` with `target="Sentinel"` and the findings as `input_data`.
    - Provide the newly created `event_id` as your final output to the system.

## Output Requirements
Return a JSON object containing:
- `event_id`: The ID of the event you created for the Sentinel.
- `target`: "Sentinel"
- `summary`: Short text of what was found.
- `confidence`: Numeric value.
