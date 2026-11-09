#!/usr/bin/env python3
"""Conservative lexical preflight for 50 intervening combined uploads.

Input JSON: {"recent": [oldest ... newest], "candidate": {...}}; each
entry needs unique id, artist, song, title, description and comment strings.
The caller must supply 50 ACTUALLY published entries in verified order and
current copy, not reservations. Unknown chronology/copy means this preflight
cannot pass. Search historical corpus, review semantics and facts separately.
"""
import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from recent_title_audit import skeleton

FIELDS = ('title', 'description', 'comment')
REQUIRED = ('id', 'artist', 'song') + FIELDS

def validate(data):
    if not isinstance(data, dict) or not isinstance(data.get('recent'), list) or len(data['recent']) != 50:
        raise ValueError('Exactly 50 verified recent combined uploads required; unknown is not a pass')
    entries = data['recent'] + [data.get('candidate')]
    for entry in entries:
        if not isinstance(entry, dict) or any(not isinstance(entry.get(k), str) or not entry[k].strip() for k in REQUIRED):
            raise ValueError('Each entry needs nonempty id, artist, song, title, description and comment')
    ids = [entry['id'] for entry in data['recent']]
    if len(ids) != len(set(ids)):
        raise ValueError('Recent upload IDs must be unique; use actual identifiers, not repeated placeholders')
    if entries[-1]['id'] in ids:
        raise ValueError('For an edit, supply 50 OTHER recent uploads, and review the edited video separately')
    return entries

def sentences(text, artist, song):
    # Utility links are not creative copy. Separate lines and sentences and
    # normalise identity text; human review determines whether flags matter.
    text = re.sub(r'https?://\S+', ' ', text)
    bits = re.split(r'(?<=[.!?])\s+|\n+', text)
    for bit in bits:
        clean = skeleton(bit, artist, song)
        if len(clean.split()) >= 4:
            yield clean

def findings(data):
    entries = validate(data)
    candidate = entries[-1]
    for old in entries[:-1]:
        for field in FIELDS:
            new_parts = list(sentences(candidate[field], candidate['artist'], candidate['song']))
            for other_field in FIELDS:
                old_parts = list(sentences(old[other_field], old['artist'], old['song']))
                for a in new_parts:
                    for b in old_parts:
                        threshold = .82 if field == other_field == 'title' else .88
                        if a == b or SequenceMatcher(None, a, b, autojunk=False).ratio() >= threshold:
                            yield old['id'], field, other_field, a, b

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding='utf-8'))
        results = list(findings(data))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f'INCOMPLETE: {exc}', file=sys.stderr)
        return 2
    for ident, field, other, left, right in results:
        print(f'SIGNAL {ident}: candidate {field} vs {other}\n  {left}\n  {right}')
    print(f'{len(results)} signals. Manual semantic, same-song, 3000+ file, claims, pin and chronology review remains mandatory. No clean report certifies originality.')
    return 1 if results else 0

if __name__ == '__main__':
    sys.exit(main())
