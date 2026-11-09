#!/usr/bin/env python3
"""Flag shared title skeletons in a list of title, artist and song triples.

Usage: python3 recent_title_audit.py triples.json
Input: a combined chronological JSON array of {"title": ..., "artist": ..., "song": ...} objects (oldest first). Unknown chronology needs manual review.
Signals require human review; this cannot certify uniqueness or predict YouTube.
"""
import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path


def tokens(value):
    return re.findall(r"[a-z0-9]+", value.lower())


def skeleton(title, artist, song):
    words = tokens(title)
    for phrase, marker in sorted(((tokens(artist), 'artist'), (tokens(song), 'song')), key=lambda x: len(x[0]), reverse=True):
        if not phrase:
            continue
        i = 0
        while i <= len(words) - len(phrase):
            if words[i:i + len(phrase)] == phrase:
                words[i:i + len(phrase)] = [marker]
                i += 1
            else:
                i += 1
    words = ['year' if re.fullmatch(r'(19|20)\d{2}', word) else word for word in words]
    return ' '.join(words)


def findings(entries, window=50, threshold=0.82):
    """Flag exact or close shapes within the preceding 50 combined uploads.

    Entries must be chronological, oldest first. At least 50 intervening uploads
    means a distance of 51; unknown order must be resolved manually.
    """
    for entry in entries:
        if not isinstance(entry, dict) or not all(isinstance(entry.get(k), str) and entry[k].strip() for k in ('title', 'artist', 'song')):
            raise ValueError('Each entry needs non-empty title, artist and song strings')
    for i, a in enumerate(entries):
        for b in entries[i + 1:i + window + 1]:
            x = skeleton(a['title'], a['artist'], a['song'])
            y = skeleton(b['title'], b['artist'], b['song'])
            if x == y or SequenceMatcher(None, x, y, autojunk=False).ratio() >= threshold:
                yield (a['title'], b['title'], f'{x} / {y}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    entries = json.loads(args.input.read_text(encoding='utf-8'))
    if not isinstance(entries, list):
        parser.error('input must be an array')
    for left, right, pattern in findings(entries):
        print(f'EXACT OR NEAR SHAPE: {left} <> {right}\n  {pattern}')
    print('Advisory only: manual review is mandatory; wording, semantics, descriptions, incomplete order and unseen/live copy may be missed.')


if __name__ == '__main__':
    main()
