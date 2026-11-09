#!/usr/bin/env python3
"""Flag shared title skeletons in a list of title, artist and song triples.

Usage: python3 recent_title_audit.py triples.json
Input: a JSON array of {"title": ..., "artist": ..., "song": ...} objects.
Signals require human review; this cannot certify uniqueness or predict YouTube.
"""
import argparse
import json
import re
from itertools import combinations
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
    return ' '.join(words)


def findings(entries):
    for a, b in combinations(entries, 2):
        if not all(isinstance(e.get(k), str) and e[k].strip() for e in (a,b) for k in ('title', 'artist', 'song')):
            raise ValueError('Each entry needs non-empty title, artist and song strings')
        x = skeleton(a['title'], a['artist'], a['song'])
        y = skeleton(b['title'], b['artist'], b['song'])
        if x == y:
            yield (a['title'], b['title'], x)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    entries = json.loads(args.input.read_text(encoding='utf-8'))
    if not isinstance(entries, list):
        parser.error('input must be an array')
    for left, right, pattern in findings(entries):
        print(f'SHARED SKELETON: {left} <> {right}\n  {pattern}')
    print('Human review still required: near-matches and unseen/live copy may be missed.')


if __name__ == '__main__':
    main()
