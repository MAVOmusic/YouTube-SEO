"""Sanity checks for the pending 12 playlist descriptions, not a release gate."""
from pathlib import Path
from collections import Counter
import re
import unittest

P = Path(__file__).resolve().parents[2] / 'TXT' / 'Playlist_Descriptions_Latest_Uploads.md'

class PlaylistRefreshTests(unittest.TestCase):
    def test_twelve_and_no_song_specific_names(self):
        text = P.read_text(encoding='utf-8')
        titles = re.findall(r'### Title\n\n```text\n(.*?)\n```', text, re.S)
        descriptions = re.findall(r'### Description\n\n```text\n(.*?)\n```', text, re.S)
        self.assertEqual((len(titles), len(descriptions)), (12, 12))
        lines = []
        for title, description in zip(titles, descriptions):
            self.assertLessEqual(len(title), 150)
            self.assertLessEqual(len(description), 5000)
            self.assertTrue(all(not w[0].islower() for w in title.replace('-', ' ').split() if w[0].isalpha()))
            self.assertNotIn('burzum', description.casefold())
            positions = [description.index(x) for x in ('kick.com/mavomusic', 'twitch.tv/mavomusic', 'discord.gg/ESGsGkN4j2')]
            self.assertEqual(positions, sorted(positions))
            cleaned = re.sub(r'https?://\S+', '', description)
            lines.extend(x.strip().casefold() for x in re.split(r'(?<=[.!?])\s+|\n+', cleaned) if x.strip())
        self.assertEqual({s: n for s, n in Counter(lines).items() if n > 1}, {})

if __name__ == '__main__':
    unittest.main()
