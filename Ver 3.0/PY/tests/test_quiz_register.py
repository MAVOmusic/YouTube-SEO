import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class QuizRegisterTest(unittest.TestCase):
    def test_recovered_questions_have_answers(self):
        text = (ROOT / 'TXT/Historical_Quiz_Questions_And_Answers.md').read_text()
        # Eight recovered historical questions plus the A-M-E-R-I-C-A Short 1892
        # and Immaculate Misconception Short 1923 proposals added 2026-11-10,
        # each recorded with its answer.
        self.assertEqual(text.count('**Answer:**'), 10)
        self.assertIn('without recoverable question', text)
        self.assertIn('Short 0147', text)
        self.assertIn('draft only', text)

    def test_playalong_created(self):
        data = json.loads((ROOT / 'TXT/Playlist_Inventory.json').read_text())
        rows = [p for p in data['playlists'] if p['genre'] == 'Play Along']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['status'], 'confirmed_created')
