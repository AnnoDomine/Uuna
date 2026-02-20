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


def get_prompt_header(role: Agents) -> dict:
    """
    Generates the standardized system prompt header for a specific agent role.

    Args:
    - role: The agent role enum.
    """
    description = AGENT_DESCRIPTIONS.get(role, "You are a specialized agent in the Library.")
    skills = get_skill_set(role)

    content = f"{description}\n\nSKILLS AND PROCEDURES:\n{skills}"

    return {
        "role": "system",
        "content": content,
    }
