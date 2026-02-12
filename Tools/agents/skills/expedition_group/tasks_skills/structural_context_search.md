# Task Skill: Structural Context Search

## Objective
To obtain community-defined schema information and headers for WoW DB2 tables to aid the Archivist's mapping process.

## Procedural Steps
1.  **Header Retrieval**: Call `get_wago_structure` for the specific table and build version.
2.  **Schema Comparison**: Check if the headers provided by Wago.tools match the column count found in the Master Archive.
3.  **Cross-Expansion Mapping**: Search for "table name changes" in Wago histories (e.g., table X became table X_V2).
4.  **Reporting**: Document discrepancies between the local database schema and the community-defined structure.

## Constraints
- **Build Matching**: Community structures vary wildly between expansions. Ensure the `build_version` parameter is strictly applied.

## Output Requirements
Return a JSON object containing:
- `headers`: List of column names found online.
- `discrepancies`: Any differences found between local and online structure.
- `confidence`: High if exact build match found, low if using a general schema.
