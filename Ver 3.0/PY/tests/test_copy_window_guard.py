import importlib.util
import sys
import unittest
from pathlib import Path

folder = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(folder))
spec = importlib.util.spec_from_file_location('copy_window_guard', folder / 'copy_window_guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

def item(i, title='An unusual bass journey for Artist Song'):
    return {'id': str(i), 'artist': 'Artist', 'song': 'Song', 'title': title,
            'description': 'The notes run around the room.', 'comment': 'Which album would you choose?'}

class WindowTests(unittest.TestCase):
    def test_incomplete_fails(self):
        with self.assertRaises(ValueError):
            list(guard.findings({'recent': [item(1)], 'candidate': item(2)}))

    def test_flags_normalised_title(self):
        old = [item(i, f'Unique text number {i} with different words') for i in range(50)]
        old[4]['title'] = 'An unusual bass journey for Artist Song'
        candidate = item('new')
        self.assertTrue(any(x[0] == '4' and x[1] == 'title' for x in guard.findings({'recent': old, 'candidate': candidate})))

    def test_duplicate_ids_fail(self):
        with self.assertRaises(ValueError):
            guard.validate({'recent': [item(1)] * 50, 'candidate': item(2)})

    def test_edit_needs_50_other_uploads(self):
        with self.assertRaises(ValueError):
            guard.validate({'recent': [item(i) for i in range(50)], 'candidate': item(3)})

    def test_links_alone_are_ignored(self):
        self.assertEqual(list(guard.sentences('https://kick.com/mavomusic', 'a', 's')), [])
