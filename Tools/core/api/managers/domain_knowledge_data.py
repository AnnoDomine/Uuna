DATAMINING_PRINCIPLES = [
    {
        "topic": "File Identifiers (FileID)",
        "context": "Modern WoW uses CASC (Content Addressable Storage Container). Files are referenced by a unique integer FileID rather than a path. The mapping is often found in 'root' files or external databases like Wago.tools."
    },
    {
        "topic": "DB2 Tables",
        "context": "DB2 files are the client-side database. They contain structured data for spells, items, quests, etc. Key tables: 'Spell.db2', 'ItemSparse.db2', 'QuestCache.db2', 'Creature.db2'."
    },
    {
        "topic": "Table Relationships",
        "context": "Tables are linked via foreign keys. Example: 'SpellEffect' links to 'Spell' via 'SpellID'. 'Item' links to 'ItemSparse' via ID. 'Creature' links to 'CreatureDisplayInfo' via 'DisplayID'."
    },
    {
        "topic": "Localization",
        "context": "Fields ending in '_lang' or localized strings are usually stored in a bitpacked format. In our DuckDB, we normalize these to readable text where possible."
    },
    {
        "topic": "Version Comparison (Diffing)",
        "context": "Datamining's core is 'Diffing' - comparing two builds to find new spells, items, or map changes. This reveals upcoming content before it is officially announced."
    },
    {
        "topic": "Binary Assets",
        "context": "Assets include .BLP (Textures), .M2 (3D Models), .WMO (World Objects), and .ADT (Terrain tiles). These are often indexed by FileID in DB2 tables like 'FileData' or 'ManifestInterfaceData'."
    }
]

DATAMINING_SOP = [
    {
        "step": "Identify Target",
        "action": "Search for keywords in common tables (e.g., search 'Sylvanas' in 'Creature' or 'Spell')."
    },
    {
        "step": "Trace References",
        "action": "If an ID is found, check which other tables reference this ID to understand the context (e.g., which spells use a specific effect)."
    },
    {
        "step": "Verify with Online Data",
        "action": "Cross-reference results with Wago.tools or Wowhead to ensure the mapping is correct."
    }
]
