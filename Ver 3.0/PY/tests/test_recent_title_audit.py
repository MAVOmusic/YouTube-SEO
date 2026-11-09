import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'recent_title_audit.py'
spec = importlib.util.spec_from_file_location('recent_title_audit', path)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class TitleAuditTests(unittest.TestCase):
    def test_song_and_artist_substitution_is_flagged(self):
        entries = [
            {'title': 'A Runaway bass moment with Linkin Park #bass', 'artist': 'Linkin Park', 'song': 'Runaway'},
            {'title': 'A Take Me Away bass moment with Avril Lavigne #bass', 'artist': 'Avril Lavigne', 'song': 'Take Me Away'},
        ]
        self.assertEqual(len(list(audit.findings(entries))), 1)

    def test_distinct_structure_is_not_an_exact_skeleton(self):
        entries = [
            {'title': 'Runaway on bass - Linkin Park', 'artist': 'Linkin Park', 'song': 'Runaway'},
            {'title': 'Avril Lavigne plays Take Me Away on bass', 'artist': 'Avril Lavigne', 'song': 'Take Me Away'},
        ]
        self.assertEqual(list(audit.findings(entries)), [])

    def test_empty_song_not_silently_accepted(self):
        entries = [{'title': 'one', 'artist': 'a', 'song': ''}, {'title': 'two', 'artist': 'b', 'song': 'b'}]
        with self.assertRaises(ValueError):
            list(audit.findings(entries))

if __name__ == '__main__':
    unittest.main()
