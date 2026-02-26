import os
from typing import Optional


def save_mermaid_diagram(name: str, content: str, build_version: Optional[str] = "N/A") -> str:
    """
    Saves a mermaid diagram string to a file in Data/maps/.

    Args:
    - name: The base name for the diagram file.
    - content: The string content of the Mermaid diagram.
    - build_version: Optional build version to append to the filename.
    """
    try:
        maps_dir = "Data/maps"
        os.makedirs(maps_dir, exist_ok=True)

        # Sanitize the name for filesystem
        safe_name = "".join([c for c in name if c.isalnum() or c in (" ", ".", "_")]).rstrip()
        file_path = os.path.join(maps_dir, f"{safe_name}_{build_version}.mmd")

        with open(file_path, "w") as f:
            f.write(content)

        return f"SUCCESS: Diagram saved to {file_path}"
    except Exception as e:
        # In a real tool, we might use a logger here
        print(f"ERROR: Failed to save mermaid diagram: {e}")
        return f"ERROR: {e}"
