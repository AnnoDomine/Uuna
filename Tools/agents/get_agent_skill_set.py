import os
import re
from functools import partial
from enum import Enum

current_file_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(current_file_dir, "skills")

ANCHOR_REGEX = r"\[\*\*.*?\*\*\]\((.+?)\)"


class Agents(str, Enum):
    ARCHIVIST = "archivist"
    CARTOGRAPHER = "cartographer"
    COURIER = "courier"
    EXPEDITION_GROUP = "expedition_group"
    LIBRARIAN = "librarian"
    OBSERVER = "observer"
    SAGES = "sages"
    SENTINEL = "sentinel"
    TINKER = "tinker"


def parse_markdown(directory: str, file: str, history=None) -> str:
    """
    Parse markdown file.

    Args:
        directory (str): directory path
        file (str): file name
        history (_type_, optional): History of already applied files. Defaults to None.

    Returns:
        str: Parsed markdonw content, incl. parsed anchor markdown files.
    """
    if history is None:
        history = set()
    filepath = os.path.normpath(os.path.join(directory, file))
    if not os.path.exists(filepath) or not filepath.endswith(".md"):
        return "No file found or file is not a markdown file."
    if filepath in history:
        return f"File already parsed. See: {filepath}"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            new_history = history.copy()
            new_history.add(filepath)
            md = f.read()
            callback = partial(replace_anchors, directory, new_history)
            return re.sub(ANCHOR_REGEX, callback, md)
    except Exception as e:
        return f"ERROR: {e} (File: {file})"


def replace_anchors(base_dir: str, history, match) -> str:
    full_path_str = match.group(1)

    if full_path_str.startswith("http"):
        # Skip if it is an online reference
        return full_path_str

    normalized_path = os.path.normpath(full_path_str)

    path_parts = normalized_path.split(os.sep)
    file_name = path_parts.pop()

    name, extension = os.path.splitext(file_name)

    # Prevent parser to parse non markdown files
    if not extension:
        file_name += ".md"
    elif extension.lower() != ".md":
        return match.group(0)

    sub_dir = os.sep.join(path_parts)
    new_dir = os.path.join(base_dir, sub_dir)

    markdown_block = (
        "\n----------------------------------------\n"
        + f"START FILE: {file_name}\n"
        + "----------------------------------------\n"
        + parse_markdown(new_dir, file_name, history)
        + "\n----------------------------------------\n"
        + f"END FILE: {file_name}\n"
        + "----------------------------------------\n"
    )

    return markdown_block


def get_skill_set(agent: Agents) -> str:
    agent_path = os.path.join(agents_dir, agent)
    return parse_markdown(agent_path, "SKILLS.md")
