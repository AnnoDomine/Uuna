WOW_EXPANSIONS = {
    "1.x": "Classic / Vanilla",
    "2.x": "The Burning Crusade (TBC)",
    "3.x": "Wrath of the Lich King (WotLK)",
    "4.x": "Cataclysm",
    "5.x": "Mists of Pandaria (MoP)",
    "6.x": "Warlords of Draenor (WoD)",
    "7.x": "Legion",
    "8.x": "Battle for Azeroth (BfA)",
    "9.x": "Shadowlands",
    "10.x": "Dragonflight",
    "11.x": "The War Within (TWW)",
    "12.x": "Midnight (Current)",
    "13.x": "The Last Titan"
}

WOW_CLASSES_SPECS = [
    {"class": "Warrior", "specs": ["Arms", "Fury", "Protection"], "role": "Tank / Melee DPS"},
    {"class": "Paladin", "specs": ["Holy", "Protection", "Retribution"], "role": "Healer / Tank / Melee DPS"},
    {"class": "Hunter", "specs": ["Beast Mastery", "Marksmanship", "Survival"], "role": "Ranged / Melee DPS"},
    {"class": "Rogue", "specs": ["Assassination", "Outlaw", "Subtlety"], "role": "Melee DPS"},
    {"class": "Priest", "specs": ["Discipline", "Holy", "Shadow"], "role": "Healer / Ranged DPS"},
    {"class": "Death Knight", "specs": ["Blood", "Frost", "Unholy"], "role": "Tank / Melee DPS"},
    {"class": "Shaman", "specs": ["Elemental", "Enhancement", "Restoration"], "role": "Ranged / Melee DPS / Healer"},
    {"class": "Mage", "specs": ["Arcane", "Fire", "Frost"], "role": "Ranged DPS"},
    {"class": "Warlock", "specs": ["Affliction", "Demonology", "Destruction"], "role": "Ranged DPS"},
    {"class": "Monk", "specs": ["Brewmaster", "Mistweaver", "Windwalker"], "role": "Tank / Healer / Melee DPS"},
    {"class": "Druid", "specs": ["Balance", "Feral", "Guardian", "Restoration"], "role": "Ranged / Melee DPS / Tank / Healer"},
    {"class": "Demon Hunter", "specs": ["Havoc", "Vengeance", "Void-Stalker (Midnight)"], "role": "Melee DPS / Tank / Ranged-Support (TBD)"},
    {"class": "Evoker", "specs": ["Augmentation", "Devastation", "Preservation"], "role": "Support / Ranged DPS / Healer"}
]

WOW_RACES = [
    {"side": "Alliance", "races": ["Human", "Dwarf", "Night Elf", "Gnome", "Draenei", "Worgen", "Pandarin", "Void Elf", "Lightforged Draenei", "Dark Iron Dwarf", "Kul Tiran", "Mechagnome"]},
    {"side": "Horde", "races": ["Orc", "Undead", "Tauren", "Troll", "Blood Elf", "Goblin", "Pandarin", "Nightborne", "Highmountain Tauren", "Mag'har Orc", "Zandalari Troll", "Vulpera"]},
    {"side": "Neutral", "races": ["Pandarin", "Dracthyr", "Earthen"]}
]

WOW_BRANCH_TYPES = [
    {"branch": "Retail", "product": "wow", "context": "The current live version. Version 12.0.x is Midnight."},
    {"branch": "PTR", "product": "wowt", "context": "Public Test Realm for upcoming patches."},
    {"branch": "Beta", "product": "wow_beta", "context": "Expansion testing (e.g., Midnight Beta)."},
    {"branch": "Alpha", "product": "wowz", "context": "Early expansion testing."},
    {"branch": "Classic Era", "product": "wow_classic_era", "context": "Vanilla WoW (1.x)."},
    {"branch": "Classic Progression", "product": "wow_classic", "context": "Classic expansions (currently evolving through Cata/MoP)."},
    {"branch": "Internal/Test", "product": "wowlivetest", "context": "Internal Blizzard testing builds."}
]

LORE_BASICS = [
    {"entity": "Arthas Menethil", "context": "The Lich King, former Prince of Lordaeron. Central to WotLK (3.x) and Shadowlands (9.x)."},
    {"entity": "Jaina Proudmoore", "context": "Powerful mage, leader of Kul Tiras. Key figure in BfA (8.x) and many other expansions."},
    {"entity": "Sylvanas Windrunner", "context": "Former Warchief, Banshee Queen. Main antagonist in Shadowlands (9.x)."},
    {"entity": "Azeroth", "context": "The world/planet, also a slumbering Titan soul."},
    {"entity": "The Jailer", "context": "Zovaal, the main antagonist of Shadowlands, ruler of the Maw."},
    {"entity": "Khagar", "context": "Apprentice of Medivh, central figure in WoD (6.x) and Legion (7.x)."},
    {"entity": "Thrall", "context": "Go'el, former Warchief of the Horde, World-Shaman."},
    {"entity": "Anduin Wrynn", "context": "King of Stormwind, son of Varian Wrynn. Key in MoP (5.x), Legion, BfA, and TWW."},
    {"entity": "The Burning Legion", "context": "Demon army led by Sargeras. Main threat in TBC (2.x) and Legion (7.x)."},
    {"entity": "The Void / Old Gods", "context": "Cosmic force, enemies of the Titans. Key figures: C'Thun, Yogg-Saron, N'Zoth (BfA)."}
]

WOW_COSMOLOGY = [
    {"force": "Order", "entity": "Titans / Pantheon", "context": "Shapers of worlds, creators of the Dragon Aspects. Key figures: Aman'Thul, Sargeras (fallen), Eonar."},
    {"force": "Disorder", "entity": "Burning Legion", "context": "Demonic army seeking to undo creation. Led by the fallen Titan Sargeras."},
    {"force": "Life", "entity": "The Wild Gods / Emerald Dream", "context": "Representation of nature and growth. Key figures: Elune, Cenarius."},
    {"force": "Death", "entity": "Shadowlands / Eternal Ones", "context": "The afterlife. Divided into realms like Bastion, Maldraxxus, Ardenweald, and Revendreth. Key: The Jailer, The Arbiter."},
    {"force": "Light", "entity": "Naaru / Holy Light", "context": "Force of healing and crystalline entities."},
    {"force": "Shadow", "entity": "Void Lords / Old Gods", "context": "Corruptive force seeking to consume the universe."}
]

WOW_GEOGRAPHY = [
    {"continent": "Eastern Kingdoms", "context": "Home of Humans, Dwarves, Gnomes, Forsaken, and Blood Elves. Key cities: Stormwind, Ironforge, Silvermoon."},
    {"continent": "Kalimdor", "context": "Home of Orcs, Trolls, Tauren, and Night Elves. Key cities: Orgrimmar, Thunder Bluff."},
    {"continent": "Northrend", "context": "Frozen waste, seat of the Lich King. Central to 3.x."},
    {"continent": "Pandaria", "context": "Hidden land of the Pandaren, sha, and mogu. Central to 5.x."},
    {"continent": "Broken Isles", "context": "Ruined site of the Tomb of Sargeras. Central to 7.x."},
    {"continent": "Zandalar / Kul Tiras", "context": "Ancient island kingdoms. Central to 8.x (BfA)."},
    {"continent": "The Dragon Isles", "context": "Ancestral home of the Dragonflights. Central to 10.x."}
]

WOW_CITIES = [
    {"city": "Stormwind", "continent": "Eastern Kingdoms", "context": "Human capital, Alliance hub."},
    {"city": "Orgrimmar", "continent": "Kalimdor", "context": "Orc capital, Horde hub."},
    {"city": "Silvermoon", "continent": "Quel'Thalas", "context": "Blood Elf capital. Central hub for Midnight (12.x)."},
    {"city": "Dalaran", "continent": "Floating", "context": "Mage city, moved multiple times (Northrend, Broken Isles)."},
    {"city": "Oribos", "continent": "Shadowlands", "context": "The Eternal City, hub for 9.x."},
    {"city": "Valdrakken", "continent": "Dragon Isles", "context": "Capital of the Aspects, hub for 10.x."},
    {"city": "Dornogal", "continent": "Khaz Algar", "context": "Earthen capital, hub for TWW (11.x)."},
    {"city": "Shattrath", "continent": "Outland", "context": "Naaru-led neutral city, hub for TBC (2.x)."}
]

WOW_FACTIONS = [
    {"name": "The Earthen Ring", "context": "Shaman organization dedicated to Azeroth's health."},
    {"name": "The Cenarion Circle", "context": "Druidic organization protecting nature."},
    {"name": "The Argent Crusade", "context": "Union of Silver Hand and Argent Dawn against the Scourge."},
    {"name": "The Illidari", "context": "Demon Hunters led by Illidan Stormrage."},
    {"name": "The Sunwell Order", "context": "Defenders of the Sunwell against the Void in Midnight (12.x)."},
    {"name": "The Dragonscale Expedition", "context": "Explorer's League and Reliquary joint venture in 10.x."}
]

WOW_FLORA_FAUNA = [
    {"type": "Dragonkin", "context": "Dragons, drakes, and whelps. Central to 10.x."},
    {"type": "The Scourge", "context": "Undead minions of the Lich King."},
    {"type": "Void-Touched", "context": "Creatures corrupted by the Void, common in Midnight (12.x)."},
    {"type": "Nry'lothian", "context": "Eldritch horrors from the Black Empire."},
    {"type": "Elementals", "context": "Sentient fire, water, earth, and air beings."}
]

WOW_HISTORY = [
    {"event": "The War of the Ancients", "context": "First invasion of the Burning Legion, leading to the Sundering of Azeroth (10,000 years ago)."},
    {"event": "The Great Sundering", "context": "The explosion of the Well of Eternity, splitting the world into continents."},
    {"event": "The Rise of the Horde", "context": "Corruption of the Orcs on Draenor and the opening of the Dark Portal."},
    {"event": "The First and Second Wars", "context": "Conflicts between the Horde and the Alliance of Lordaeron."},
    {"event": "The Third War", "context": "Return of the Burning Legion and the rise of the Scourge (Warcraft III)."},
    {"event": "The Shattering (Cataclysm)", "context": "Deathwing's return and the devastation of Azeroth (4.x)."},
    {"event": "The Fourth War", "context": "War between Horde and Alliance during BfA (8.x)."},
    {"event": "The Worldsoul Saga", "context": "Trilogy starting with TWW (11.x), Midnight (12.x), and The Last Titan (13.x)."}
]

CORPORATE_CONTEXT = [
    {"entity": "Blizzard Entertainment", "context": "Developer of World of Warcraft. Founded 1991."},
    {"entity": "Activision Blizzard", "context": "Parent company formed by the merger of Activision and Vivendi Games (Blizzard's parent) in 2008."},
    {"entity": "Microsoft", "context": "Acquired Activision Blizzard in 2023. WoW is now part of the Xbox/Microsoft ecosystem."},
    {"entity": "Metzen", "context": "Chris Metzen, the 'father' of Warcraft lore, returned as Executive Creative Director for the Worldsoul Saga."}
]