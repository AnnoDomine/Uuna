import sys
from typing import Union

from loguru import logger

from Tools.agents.get_agent_skill_set import Agents

# UNIFIED LOG SCHEMA
logger.remove()
LOG_FORMAT = "[{time:YYYY-MM-DD HH:mm:ss} - {level} - {extra[process]} - {extra[agent]}]: {message}"

def log_filter(record):
    """Ensures that required extra fields exist to avoid KeyError in formatting."""
    if "process" not in record["extra"]:
        record["extra"]["process"] = "N/A"
    if "agent" not in record["extra"]:
        record["extra"]["agent"] = "CORE"
    return True

logger.add(sys.stderr, format=LOG_FORMAT, level="INFO", filter=log_filter)
logger.add("Data/logs/debug_agents.log", format=LOG_FORMAT, rotation="10 MB", level="INFO", filter=log_filter)
logger.add("Data/logs/error_agents.log", format=LOG_FORMAT, rotation="10 MB", level="ERROR", filter=log_filter)


class Debugger:
    def __init__(self):
        self.logger = logger

    def add_log(self, msg: str, agent: Union[Agents, str], level: str = "INFO", process: str = "N/A", **kwargs):
        """
        Add a log entry with unified schema.
        
        Args:
            msg (str): The message to log.
            agent (Union[Agents, str]): The source (Agent Enum or Service Name string).
            level (str): Log level (INFO, ERROR, DEBUG, etc.).
            process (str): Sub-process or context name.
            **kwargs: Additional metadata for loguru bind.
        """
        agent_name = agent.value if isinstance(agent, Agents) else str(agent)
        self.logger.bind(agent=agent_name, process=process, **kwargs).log(level.upper(), msg)
