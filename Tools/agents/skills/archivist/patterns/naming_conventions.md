# Pattern: Naming Conventions

## Suffix Patterns
- **`ID`**: Points to a primary key in another table. Usually, the table name is the same as the column name minus the 'ID' suffix (e.g., `QuestID` -> `Quest`).
- **`flags` / `bit`**: Integer field used as a bitmask. Should not be mapped.
- **`msec` / `time`**: Integer field representing milliseconds or game ticks.
- **`lang` / `text`**: Localized string reference.
- **`Parent`**: Reference to the same table (recursive relationship).

## Pluralization Logic
If a column name like `SpellID` exists, check for both `Spell` and `Spells` in the target tables. Some WoW builds use plural names for main tables.

## Recursive Relationships
Columns like `NextID` or `ParentID` often point back to the ID column of the same table.
