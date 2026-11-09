from pathlib import Path
import re
import unittest

FILE = Path(__file__).resolve().parents[2] / 'TXT' / 'Play_Along_Playlist_And_Shorts_CTA.md'

class PlayAlongCtaTests(unittest.TestCase):
    def test_each_short_has_distinct_related_video_line(self):
        text = FILE.read_text(encoding='utf-8')
        sections = re.findall(r'^### (?:Burzum|MIW) Short \d{4}\n\n```text\n(.*?)\n```', text, re.M | re.S)
        self.assertEqual(len(sections), 5)
        calls = []
        for description in sections:
            matches = [x.strip() for x in description.splitlines() if 'related video' in x.lower()]
            self.assertEqual(len(matches), 1)
            calls.append(matches[0])
        self.assertEqual(len(set(calls)), 5)
        self.assertNotIn('disguise', sections[2].split('\n\n')[0].lower())

if __name__ == '__main__':
    unittest.main()
