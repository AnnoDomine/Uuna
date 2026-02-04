import unittest
from online_researcher import sanitize_html

class TestSanitization(unittest.TestCase):
    def test_script_removal(self):
        html = "<div>Safe</div><script>alert('evil')</script>"
        result = sanitize_html(html)
        self.assertNotIn("script", result)
        self.assertNotIn("alert", result)
        self.assertIn("Safe", result)

    def test_style_removal(self):
        html = "<style>.body { color: red; }</style><p>Content</p>"
        result = sanitize_html(html)
        self.assertNotIn("color: red", result)
        self.assertIn("Content", result)

    def test_iframe_removal(self):
        html = "<iframe src='malicious.com'></iframe><p>Safe</p>"
        result = sanitize_html(html)
        self.assertNotIn("iframe", result)
        self.assertNotIn("malicious", result)
        self.assertIn("Safe", result)

    def test_structural_integrity(self):
        html = "<h1>Title</h1><p>Paragraph</p><ul><li>Item 1</li></ul>"
        result = sanitize_html(html)
        self.assertIn("Title", result)
        self.assertIn("Paragraph", result)
        self.assertIn("Item 1", result)

if __name__ == "__main__":
    unittest.main()
