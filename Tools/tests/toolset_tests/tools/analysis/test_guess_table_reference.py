# Tools/tests/toolsets/tools/analysis/test_guess_table_reference.py
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from Tools.toolsets.tools.analysis.guess_table_reference import guess_table_reference


class TestGuessTableReference(unittest.TestCase):
    def setUp(self):
        self.mock_tables = [
            "SpellName",
            "SpellFocusObject",
            "Item",
            "ItemSparse",
            "QuestV2",
            "ZoneIntroMusicTable",
            "SomeOtherTable",
        ]

    def test_direct_match(self):
        """Should find a direct, case-insensitive match with confidence 1.0."""
        suggestions = guess_table_reference("item", self.mock_tables)
        self.assertIn({"table": "Item", "reason": "Direct Match (case-insensitive)", "confidence": 1.0}, suggestions)

    def test_alias_match(self):
        """Should find a match through the hardcoded alias list."""
        suggestions = guess_table_reference("Spell", self.mock_tables)
        # It will also find "SpellFocusObject" as a fuzzy match, so we check that the alias is ranked higher
        self.assertTrue(any(s["table"] == "SpellName" and s["reason"] == "Alias Match" for s in suggestions))
        self.assertEqual(suggestions[0]["table"], "SpellName")
        self.assertEqual(suggestions[0]["confidence"], 0.98)

    def test_suffix_match(self):
        """Should find a match by adding a suffix (even if another rule also finds it)."""
        suggestions = guess_table_reference("Item", self.mock_tables)
        # Direct match for "Item" will be first
        self.assertEqual(suggestions[0]["table"], "Item")
        # Just assert that "ItemSparse" is in the list of suggested tables
        self.assertTrue(any(s["table"] == "ItemSparse" for s in suggestions))

    def test_fuzzy_match(self):
        """Should find a close match using difflib."""
        suggestions = guess_table_reference("SpellFocusObj", self.mock_tables)
        self.assertGreater(len(suggestions), 0)
        self.assertEqual(suggestions[0]["table"], "SpellFocusObject")
        self.assertEqual(suggestions[0]["reason"], "Fuzzy Match")

    def test_substring_match(self):
        """Should find a table that contains the potential name as a substring."""
        suggestions = guess_table_reference("Music", self.mock_tables)
        self.assertTrue(
            any(s["table"] == "ZoneIntroMusicTable" and s["reason"] == "Substring Match" for s in suggestions)
        )

    def test_sorting_order(self):
        """Ensures that higher confidence matches are ranked first."""
        # "Spell" will trigger multiple heuristics
        suggestions = guess_table_reference("Spell", self.mock_tables)

        # Expected order: Alias > Fuzzy > Substring
        self.assertEqual(suggestions[0]["table"], "SpellName")  # Alias, highest confidence
        self.assertEqual(suggestions[0]["confidence"], 0.98)

        self.assertEqual(suggestions[1]["table"], "SpellFocusObject")  # Fuzzy, next highest
        self.assertTrue(suggestions[1]["confidence"] < 0.98)

    def test_no_match(self):
        """Should return an empty list if no reasonable match is found."""
        suggestions = guess_table_reference("NonExistentXYZ", self.mock_tables)
        self.assertEqual(len(suggestions), 0)


if __name__ == "__main__":
    unittest.main()
