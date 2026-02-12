# Task Skill: Column Discovery

## Objective
To determine the semantic meaning and functional role of a specific database column within a WoW DB2 table.

## Procedural Steps
1.  **Analyze Samples**: Examine at least 10 data samples from the column to identify patterns (e.g., small integers, large hashes, localized strings).
2.  **Statistcial Review**: Check min/max values and distinct ratios. A high distinct ratio often indicates a primary key or a unique name.
3.  **Expansion Context**: Compare the current build's data with previous builds. If values only appear in a specific expansion (e.g., Dragonflight IDs), the column is likely expansion-specific.
4.  **Semantic Guessing**:
    - Endings in `ID`: Reference to another table.
    - Endings in `msec`: Time durations.
    - Endings in `flags`: Bitmask fields.
5.  **Online Verification**: Use `search_wow_wiki` and `get_wago_structure` to cross-reference findings with public datamining knowledge.

## Output Requirements
Return a JSON object containing:
- `discovery`: A detailed explanation of the column's purpose.
- `type`: Either `structure` (mapping candidate) or `content` (standalone value).
- `confidence`: Numeric value (0.0 to 1.0).
