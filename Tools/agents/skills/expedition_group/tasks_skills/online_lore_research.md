# Task Skill: Online Lore Research

## Objective
To find and extract relevant historical and gameplay context for specific WoW entities (NPCs, Spells, Quests, Items) from trusted external wikis.

## Procedural Steps
1.  **Search Strategy**: Use the `search_wow_wiki` tool with specific keywords (e.g., "Quest: The Missing Diplomat" instead of just "The Missing Diplomat").
2.  **Content Retrieval**: Fetch the top 1-2 search results using the `fetch_web_content` tool.
3.  **Entity Identification**: Scan the retrieved text for key entities:
    - Primary NPC/Actor
    - Location/Zone
    - Faction requirement
    - Expansion of introduction
4.  **Verification**: If the data contradicts the Archivist's findings (e.g., wiki says Quest is in Northrend, but Archivist found it in a Vanilla build), flag the conflict for the **Sages**.

## Constraints
- **Sanitization**: Only use text that has been passed through the project's HTML sanitizer.
- **Source Link**: Every finding must be attributed to a specific URL.

## Output Requirements
Return a JSON object containing:
- `lore_facts`: List of confirmed context points.
- `source_urls`: List of URLs used.
- `confidence`: Confidence based on the clarity of the source.
