"""Regression tests for preserved-artist-comment extraction."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('long_form_gate', Path(__file__).resolve().parents[1] / 'long_form_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

PREFIX = ''.join(f'## {name}\n\n```text\nvalue\n```\n\n' for name in ('TITLE', 'DESCRIPTION', 'TAGS'))
SUFFIX = '\n## CORRECT GENRES\n\n- Rock\n'


class PreservedPinTest(unittest.TestCase):
    def extract(self, pin):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'copy.md'
            path.write_text(PREFIX + pin + SUFFIX, encoding='utf-8')
            return gate.extract(path)

    def test_preserved_comment_is_hashed_not_instruction(self):
        fields = self.extract('## PINNED COMMENT - DO NOT REPLACE\n\n> Preserve it.\n> PRESERVED ARTIST COMMENT: @artist: "Hello!"\n')
        self.assertEqual(fields['pinned comment'], '@artist: "Hello!"')
        self.assertEqual(gate.digest(fields['pinned comment']), gate.digest('@artist: "Hello!"'))

    def test_missing_marker_rejected(self):
        with self.assertRaises(ValueError):
            self.extract('## PINNED COMMENT\n\n> Preserve it.\n')

    def test_normal_pin_unchanged(self):
        fields = self.extract('## PINNED COMMENT\n\n```text\nA question?\n```\n')
        self.assertEqual(fields['pinned comment'], 'A question?')


if __name__ == '__main__':
    unittest.main()

class InventoryScopeTest(unittest.TestCase):
    def test_short_ids_do_not_collide_with_long_form_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for category in ('_0001 Long Form', '_0002 Short Form'):
                path = root / '_All Songs' / category / '0001 - 0100' / '0001 - example' / '_03 - Copy.md'
                path.parent.mkdir(parents=True)
                path.write_text('sample', encoding='utf-8')
            original = gate.ROOT
            try:
                gate.ROOT = root
                items = gate.inventory()
                self.assertEqual(len(items['0001']), 1)
                self.assertIn('_0001 Long Form', str(items['0001'][0]))
            finally:
                gate.ROOT = original
