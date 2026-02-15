# Tools/tests/toolsets/tools/research/test_research_tools.py
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from Tools.toolsets.tools.research.fetch_web_content import fetch_web_content, sanitize_html
from Tools.toolsets.tools.research.search_wow_wiki import search_wow_wiki
from Tools.toolsets.tools.research.get_wago_structure import get_wago_structure
from Tools.core.db_client import DBResult


class TestResearchTools(unittest.TestCase):
    def test_sanitize_html(self):
        html = "<html><body><script>alert('xss')</script><h1>Title</h1><p>Content</p></body></html>"
        sanitized = sanitize_html(html)
        self.assertNotIn("script", sanitized)
        self.assertIn("Title", sanitized)
        self.assertIn("Content", sanitized)

    @patch("requests.get")
    @patch("Tools.toolsets.tools.research.fetch_web_content.db")
    def test_fetch_web_content_cached(self, mock_db, mock_get):
        # Mock cache hit
        mock_result = DBResult({"results": [("Cached Content",)]})
        mock_db.execute.return_value = mock_result

        result = fetch_web_content("http://test.com")

        self.assertEqual(result, "Cached Content")
        mock_get.assert_not_called()

    @patch("requests.get")
    @patch("Tools.toolsets.tools.research.search_wow_wiki.db")
    def test_search_wow_wiki(self, mock_db, mock_get):
        # Mock cache miss
        mock_db.execute.return_value = DBResult({"results": []})

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = ["query", ["Title"], ["Desc"], ["http://wiki/Title"]]
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = search_wow_wiki("test query")

        self.assertEqual(result, ["http://wiki/Title"])
        self.assertEqual(mock_get.call_count, 1)

    @patch("requests.get")
    @patch("Tools.toolsets.tools.research.get_wago_structure.db")
    def test_get_wago_structure(self, mock_db, mock_get):
        # Mock cache miss
        mock_db.execute.return_value = DBResult({"results": []})

        # Mock streaming CSV response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = ["ID,Name,Type"]
        mock_get.return_value.__enter__.return_value = mock_response

        result = get_wago_structure("Table", "10.0.0")

        self.assertIn("ID,Name,Type", result)


if __name__ == "__main__":
    unittest.main()
