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

    def test_year_substitution_flagged(self):
        entries = [
            {'title': 'Back to 2004 with Alpha - One on bass', 'artist': 'Alpha', 'song': 'One'},
            {'title': 'Back to 2014 with Beta - Two on bass', 'artist': 'Beta', 'song': 'Two'},
        ]
        self.assertEqual(len(list(audit.findings(entries))), 1)

    def test_requires_fifty_intervening_uploads(self):
        one = {'title': 'A One moment with Alpha', 'artist': 'Alpha', 'song': 'One'}
        two = {'title': 'A Two moment with Beta', 'artist': 'Beta', 'song': 'Two'}
        fillers = [{'title': f'Unique arrangement {i} xxx', 'artist': f'Artist {i}', 'song': f'Track {i}'} for i in range(50)]
        pair = lambda items: [x for x in audit.findings(items) if x[0] == one['title'] and x[1] == two['title']]
        self.assertTrue(pair([one] + fillers[:49] + [two]))
        self.assertFalse(pair([one] + fillers + [two]))

    def test_empty_song_not_silently_accepted(self):
        entries = [{'title': 'one', 'artist': 'a', 'song': ''}, {'title': 'two', 'artist': 'b', 'song': 'b'}]
        with self.assertRaises(ValueError):
            list(audit.findings(entries))

if __name__ == '__main__':
    unittest.main()
