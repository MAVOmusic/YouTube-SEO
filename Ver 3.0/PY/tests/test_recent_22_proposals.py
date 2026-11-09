"""Local copy checks; not a substitute for live metadata or the 50-upload audit."""
from pathlib import Path
import re
import unittest
from collections import Counter

FILE = Path(__file__).resolve().parents[2] / 'TXT' / 'Recent_Uploads_22_Replacement_Proposals.md'

class RecentCopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = FILE.read_text(encoding='utf-8')

    def blocks(self, heading):
        return re.findall(r'### ' + heading + r'\n\n```text\n(.*?)\n```', self.text, re.S)

    def test_package_and_character_limits(self):
        titles = self.blocks('Title')
        tags = self.blocks(r'Tags \(\d+/500 characters\)')
        descriptions = self.blocks('Description')
        pins = self.blocks('Pinned comment - proposal')
        self.assertEqual([len(titles), len(descriptions), len(tags), len(pins)], [22]*4)
        self.assertTrue(all(len(title) <= 100 for title in titles))
        self.assertTrue(all(len(tag) <= 500 and 'rocksmith 2014 remastered' in tag for tag in tags))
        for description in descriptions:
            positions = [description.index(url) for url in ('kick.com/mavomusic', 'twitch.tv/mavomusic', 'discord.gg/ESGsGkN4j2')]
            self.assertEqual(positions, sorted(positions))

    def test_no_exact_repeated_sentences_or_lines(self):
        lines = []
        for block in self.blocks('Description') + self.blocks('Pinned comment - proposal'):
            block = re.sub(r'https?://\S+', '[URL]', block)
            lines.extend(s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', block) if s.strip())
        repeats = {line: count for line, count in Counter(lines).items() if count > 1}
        self.assertEqual(repeats, {})

if __name__ == '__main__':
    unittest.main()
