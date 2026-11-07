import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "check_song_catalogues.py"
spec = importlib.util.spec_from_file_location("song_catalogues", MODULE_PATH)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = (("short", "Short.md", "_0002 Short Form", "Short Form", 2),)
        self.catalogue = self.root / "Short.md"
        self.video = self.root / "_All Songs/_0002 Short Form/0001 - 0100/0001 - 0010/0001 - Artist - Song (Short Form)"
        self.video.mkdir(parents=True)
        (self.video / "_03 - Copy.md").write_text("## TITLE (12 characters)\n\n```text\nA | B\n```\n")
        self.catalogue.write_text("| 0001 | Artist - Song [reserved] | A \\| B |\n| 0002 | N/A | N/A |\n")

    def run_check(self):
        with patch.object(checker, "CONFIGS", self.config), contextlib.redirect_stdout(io.StringIO()):
            return checker.check(self.root)

    def test_valid_escaped_title_and_reservation(self):
        self.assertEqual(self.run_check(), [])

    def test_outdated_copy_is_rejected(self):
        self.catalogue.write_text("| 0001 | Artist - Song | Old title |\n| 0002 | N/A | N/A |\n")
        self.assertTrue(any("title differs" in error for error in self.run_check()))

    def test_missing_and_duplicate_numbers_are_rejected(self):
        self.catalogue.write_text("| 0001 | Artist - Song | A \\| B |\n| 0001 | Artist - Song | A \\| B |\n")
        errors = self.run_check()
        self.assertTrue(any("duplicate" in error for error in errors))
        self.assertTrue(any("missing" in error for error in errors))

    def test_unregistered_folder_is_rejected(self):
        self.catalogue.write_text("| 0001 | N/A | A \\| B |\n| 0002 | N/A | N/A |\n")
        self.assertTrue(any("identity differs" in error for error in self.run_check()))


if __name__ == "__main__":
    unittest.main()
