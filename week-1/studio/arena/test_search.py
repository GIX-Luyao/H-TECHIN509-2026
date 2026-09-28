"""Run with: python -m unittest -v. Failures are intentional at the start."""
import unittest
from pathlib import Path
from search import Library


class SearchChecks(unittest.TestCase):
    def setUp(self):
        self.library = Library(Path(__file__).parent / "data" / "documents.json")

    def test_normal_query(self):
        self.assertEqual(self.library.search("vacation")[0]["source"], "leave.md")

    def test_unknown_query(self):
        self.assertEqual(self.library.search("spaceship"), [])

    def test_case_insensitive(self):
        self.assertEqual(len(self.library.search("PASSWORD")), 2)

    def test_trim_query(self):
        self.assertEqual(len(self.library.search(" password  ")), 2)

    def test_blank_query(self):
        self.assertEqual(self.library.search(""), [])
        self.assertEqual(self.library.search("   "), [])

    def test_result_limit(self):
        self.assertEqual(len(self.library.search("password", limit=1)), 1)

    def test_zero_limit(self):
        self.assertEqual(self.library.search("password", limit=0), [])


if __name__ == "__main__":
    unittest.main()
