# Tools/tests/toolsets/tools/filesystem/test_save_mermaid_diagram.py
import unittest
from unittest.mock import patch, mock_open
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from toolsets.tools.filesystem.save_mermaid_diagram import save_mermaid_diagram


class TestSaveMermaidDiagram(unittest.TestCase):
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_saves_file_correctly(self, mock_file, mock_makedirs):
        """
        Tests that the tool constructs the correct path and writes the correct content.
        """
        # --- Test Data ---
        diagram_name = "Test Build Map"
        diagram_content = "erDiagram\n    TABLE1 ||--o{ TABLE2 : relationship"
        build_version = "1.2.3"

        # --- Expected Values ---
        expected_dir = "Data/maps"
        expected_filename = "Test Build Map_1.2.3.mmd"
        expected_path = os.path.join(expected_dir, expected_filename)

        # --- Test Execution ---
        result = save_mermaid_diagram(diagram_name, diagram_content, build_version)

        # --- Assertions ---
        # 1. Assert that makedirs was called for the correct directory
        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)

        # 2. Assert that open was called to write to the correct file path
        mock_file.assert_called_once_with(expected_path, "w")

        # 3. Assert that the correct content was written to the file
        mock_file().write.assert_called_once_with(diagram_content)

        # 4. Assert that the success message is correct
        self.assertEqual(result, f"SUCCESS: Diagram saved to {expected_path}")

    @patch("os.makedirs", side_effect=OSError("Test Error"))
    def test_handles_exception(self, mock_makedirs):
        """
        Tests that the tool gracefully handles exceptions during file operations.
        """
        result = save_mermaid_diagram("test", "content")
        self.assertTrue(result.startswith("ERROR:"))


if __name__ == "__main__":
    unittest.main()
