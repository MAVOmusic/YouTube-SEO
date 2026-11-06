#!/usr/bin/env python3
"""Long-form release gate. Evidence attestations require human verification.

Usage: python3 'Ver 3.0/PY/long_form_gate.py' --report 0001 0002
       python3 'Ver 3.0/PY/long_form_gate.py' --check 0001 0002
See TXT/Long_Form_Release_Gate.txt for the review record format and limits.
"""
import argparse
import glob
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / 'Ver 3.0' / 'TXT' / 'Long_Form_Reviews'
SURFACES = ('title', 'description', 'tags', 'pinned comment', 'genres')


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def extract(path):
    text = path.read_text(encoding='utf-8')
    fields = {}
    for name in SURFACES[:-1]:
        match = re.search(r'^## ' + re.escape(name) + r'\b[^\n]*\n(?:(?!^## ).)*?```(?:text)?\s*\n(.*?)\n```', text, re.I | re.M | re.S)
        if not match and name == 'pinned comment':
            # An existing artist comment is not creator paste copy. Hash its
            # explicitly marked historical text without prompting replacement.
            match = re.search(r'^## PINNED COMMENT\b[^\n]*\n(?:(?!^## ).)*?^> PRESERVED ARTIST COMMENT: ([^\n]+)$', text, re.I | re.M | re.S)
        if not match:
            raise ValueError(f'{path}: missing {name} fenced block or preserved artist comment')
        fields[name] = match.group(1)
    match = re.search(r'^## CORRECT GENRES\b[^\n]*\n(.*?)(?=^## |\Z)', text, re.I | re.M | re.S)
    if not match or not re.search(r'^\s*-\s+\S', match.group(1), re.M):
        raise ValueError(f'{path}: missing correct genres list')
    fields['genres'] = match.group(1).strip()
    return fields


def inventory():
    found = defaultdict(list)
    for p in ROOT.glob('_All Songs/_0001 Long Form/**/_03 - Copy.md'):
        m = re.match(r'^(\d{4}) - ', p.parent.name)
        if m:
            found[m.group(1)].append(p)
    return found


def words(s):
    s = re.sub(r'https?://\S+', ' ', s.lower())
    return re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?", s)


def collisions(target, fields, corpus):
    # A signal to investigate, not a decision: names, titles and common phrases recur.
    output = []
    for ident, other in sorted(corpus.items()):
        if ident == target:
            continue
        for name in ('title', 'description', 'pinned comment'):
            a = words(fields[name])
            agrams = {tuple(a[i:i+5]) for i in range(max(0, len(a)-4))}
            for other_name in ('title', 'description', 'pinned comment'):
                b = words(other[other_name])
                bgrams = {tuple(b[i:i+5]) for i in range(max(0, len(b)-4))}
                for gram in sorted(agrams & bgrams):
                    output.append(f'{ident} | {name} vs {other_name} | {" ".join(gram)}')
    return output


def report(ident, paths, corpus):
    fields = corpus[ident]
    matches = collisions(ident, fields, corpus)
    print(f'\nCO-{ident}: {paths[ident][0].relative_to(ROOT)}')
    print('Surface SHA-256:')
    for name in SURFACES:
        print(f'  {name}: {digest(fields[name])}')
    print(f'Collision report SHA-256: {digest(chr(10).join(matches))}')
    print(f'Cross-video five-word signals: {len(matches)}')
    for item in matches:
        print('  ' + item)
    return fields, matches


def check(ident, fields, matches):
    path = RECORDS / f'{ident}.json'
    if not path.is_file():
        return [f'missing review record {path.relative_to(ROOT)}']
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('record must be an object')
    except (OSError, ValueError) as exc:
        return [f'invalid review record: {exc}']
    errors = []
    hashes = data.get('surface_sha256', {})
    if not isinstance(hashes, dict):
        hashes = {}
    for name in SURFACES:
        if hashes.get(name) != digest(fields[name]):
            errors.append(f'{name}: missing or stale surface hash')
    claims = data.get('claims')
    if not isinstance(claims, list) or not claims:
        errors.append('missing claim-by-claim evidence list')
    else:
        for i, claim in enumerate(claims, 1):
            if not isinstance(claim, dict) or claim.get('surface') not in SURFACES or not all(isinstance(claim.get(k), str) and claim[k].strip() for k in ('claim', 'source', 'assessment')):
                errors.append(f'claim {i}: requires surface, claim, source and assessment')
    for key in ('reviewer', 'reviewed_at', 'distinct_fact_and_source', 'uniqueness_assessment', 'uncertainties_and_removed_claims'):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f'missing {key}')
    checks = data.get('reviewed_surfaces', {})
    for name in SURFACES:
        if not isinstance(checks, dict) or checks.get(name) is not True:
            errors.append(f'{name}: manual review not attested')
    if data.get('collision_report_sha256') != digest('\n'.join(matches)):
        errors.append('collision report missing or stale: review all signals against current corpus')
    if data.get('all_claims_checked') is not True or data.get('cross_song_uniqueness_checked') is not True:
        errors.append('claim-by-claim and cross-song uniqueness attestations required')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--report', action='store_true')
    modes.add_argument('--check', action='store_true')
    parser.add_argument('ids', nargs='+', help='four-digit CO identifiers')
    args = parser.parse_args()
    paths = inventory()
    errors = []
    for ident in args.ids:
        if not re.fullmatch(r'\d{4}', ident) or len(paths.get(ident, [])) != 1:
            errors.append(f'{ident}: expected exactly one matching copy file')
    if errors:
        print('\n'.join(errors)); return 1
    corpus = {}
    for ident, entries in sorted(paths.items()):
        if len(entries) != 1:
            errors.append(f'{ident}: duplicate copy files in comparison corpus')
            continue
        try:
            corpus[ident] = extract(entries[0])
        except ValueError as exc:
            # Legacy files may lack split genre headings; still compare their written surfaces.
            if ident in args.ids:
                errors.append(str(exc)); continue
            text = entries[0].read_text(encoding='utf-8')
            item = {}
            for name in ('title', 'description', 'pinned comment'):
                m = re.search(r'^## ' + re.escape(name) + r'\b[^\n]*\n(?:(?!^## ).)*?```(?:text)?\s*\n(.*?)\n```', text, re.I | re.M | re.S)
                if not m:
                    errors.append(f'{ident}: cannot compare {name}'); break
                item[name] = m.group(1)
            else:
                corpus[ident] = item
    if errors:
        print('\n'.join(errors)); return 1
    for ident in args.ids:
        fields, matches = report(ident, paths, corpus)
        if args.check:
            errors.extend(f'CO-{ident}: {err}' for err in check(ident, fields, matches))
    if errors:
        print('\nFAIL - do not release:\n' + '\n'.join(errors)); return 1
    if args.check:
        print('\nRecord gate passed. Human evidence and originality assessments are not independently verified by this program.')
    else:
        print('\nReport only: this does NOT approve any copy. Review every claim and signal, then record and run --check.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
