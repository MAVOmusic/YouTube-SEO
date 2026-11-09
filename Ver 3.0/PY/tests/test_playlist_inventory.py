import importlib.util
import json
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('playlist_inventory', root / 'playlist_inventory.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class PlaylistInventoryTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(mod.REGISTRY.read_text(encoding='utf-8'))

    def test_confirmed_and_unconfirmed(self):
        self.assertEqual(mod.lookup(self.data, 'ambient', 'shorts')[0]['status'], 'confirmed_created')
        self.assertEqual(mod.lookup(self.data, 'metalcore', 'shorts')[0]['status'], 'confirmed_created')
        self.assertEqual(mod.lookup(self.data, 'not a real genre', 'shorts'), [])

    def test_no_duplicate_genre_format_keys(self):
        keys = [(mod.normalize(x['genre']), x['format']) for x in self.data['playlists']]
        self.assertEqual(len(keys), len(set(keys)))

    def test_all_confirmed_have_evidence(self):
        self.assertTrue(all(x['evidence'] for x in self.data['playlists'] if x['status'] == 'confirmed_created'))
