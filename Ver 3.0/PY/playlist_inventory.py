#!/usr/bin/env python3
"""Look up a genre/format before proposing or creating a playlist.

This local registry is incomplete and not a live Studio lookup. A missing entry
or unconfirmed proposal is never proof that a playlist does not already exist.
"""
import argparse
import json
import re
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / 'TXT' / 'Playlist_Inventory.json'

def normalize(value):
    return re.sub(r'[^a-z0-9]+', ' ', value.casefold()).strip()

def lookup(registry, genre, format_name):
    return [x for x in registry['playlists'] if normalize(x['genre']) == normalize(genre) and x['format'] == format_name]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('genre')
    parser.add_argument('format', choices=['shorts', 'long_form'])
    args = parser.parse_args()
    data = json.loads(REGISTRY.read_text(encoding='utf-8'))
    rows = lookup(data, args.genre, args.format)
    if not rows:
        print('UNKNOWN: Search current Studio inventory and ask before creating; absence here does not prove absence on YouTube.')
        return
    for row in rows:
        print(f"{row['status']}: {row['title']}\n  {row['evidence']}\n  Description: {row['description_status']}")
    print('Check live Studio and preserve existing playlist links; names and status can change.')

if __name__ == '__main__':
    main()
