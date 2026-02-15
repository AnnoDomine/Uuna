from Tools.agents.get_agent_skill_set import Agents, get_skill_set

AGENT_DESCRIPTIONS = {
    Agents.ARCHIVIST: "You are the Archivist, an expert in Azeroth's history and game mechanics.",
    Agents.CARTOGRAPHER: "You are The Cartographer, expert in data visualization.",
    Agents.COURIER: "You are The Courier, the heart of the library's orchestration system.",
    Agents.EXPEDITION_GROUP: "You are The Expedition Group, the research arm of the library.",
    Agents.LIBRARIAN: "You are The Librarian, the bridge between the human user and the library's archive.",
    Agents.OBSERVER: "You are The Observer, the final arbiter of quality.",
    Agents.SAGES: "You are The Sages, the final authority on logical truth.",
    Agents.SENTINEL: "You are The Sentinel, the shield to protect the system.",
    Agents.TINKER: "You are The Tinker, the quantitative analyst of the library.",
}


def getPromptHeader(role: Agents):
    return {
        "role": "system",
        "content": f"{AGENT_DESCRIPTIONS.get(role)}\n\nSKILLS:\n{get_skill_set(role)}",
    }
