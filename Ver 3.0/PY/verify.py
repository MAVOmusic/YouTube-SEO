#!/usr/bin/env python3
"""
MAVOmusic Workspace Verification Script  (VER 3.0 - 2026-11-01)
================================================================
Tier-1 gate of the two-tier pre-ship gate (Tier-2 = diversity_guard.py).

VER 3.0 changes vs v8:
  * Portable ROOT - works in /home/user, in a repo subfolder, or any sandbox.
    Override with the MAVO_ROOT environment variable if ever needed.
  * HARD FAIL on duplication. Every uniqueness check now sets the exit code.
    (v8 printed "DUPES: [...]" and still exited 0 - a silent-gate hole that
    let the 0074/0085 `monstercat` Shorts-opener collision ship.)
  * NEW check: `**Folder Location:**` line must byte-match the real path.
  * NEW check: Section 1 letter convention ([A-Z] / 0-9 / Special Characters).
  * NEW check: Section 9 tidy-root scan (no .py, no images in workspace root).

Exit code 0 = PASS. Exit code 1 = FAIL (list printed above the summary).
Run from anywhere:  python3 PY/verify.py      (or: bash verify.sh)
"""

import re
import glob
import collections
import os
import sys
import unicodedata

ROOT = os.environ.get('MAVO_ROOT') or os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))

FAILS = []


def fail(msg):
    FAILS.append(msg)


def g(lab, src):
    """Pull a ```text fenced block that follows '### <lab>:'."""
    patterns = [
        r'### ' + re.escape(lab) + r':\s*\n```text\s*\n(.*?)\n```',
        r'### ' + re.escape(lab) + r':\s*\n```\s*\n(.*?)\n```',
        r'### ' + re.escape(lab) + r':\s*\n(.*?)\n```text',
    ]
    for p in patterns:
        m = re.search(p, src, re.DOTALL)
        if m:
            return m.group(1).strip()
    return ''


def audit(name, items):
    """Duplicate report. Any collision is a FAIL (VER 3.0 hardening)."""
    counter = collections.Counter(items)
    dupes = [x for x, c in counter.items() if c > 1]
    if dupes:
        print(f'{name:35s}: {len(items):3d} -> DUPES: {dupes}')
        fail(f'{name}: duplicate values {dupes}')
    else:
        print(f'{name:35s}: {len(items):3d} -> all unique \u2713')


def expected_letter(artist_folder):
    """Section 1 letter convention (v1.90 codified)."""
    named = unicodedata.normalize('NFKD', artist_folder)
    named = ''.join(c for c in named if not unicodedata.combining(c))
    first = named[0]
    if first.isdigit():
        return '0-9'
    if first.isalpha():
        return first.upper()
    return 'Special Characters'


def main():
    os.chdir(ROOT)
    print("=" * 50)
    print("MAVOmusic Workspace Verification (VER 3.0)")
    print("=" * 50)
    print()

    files = sorted(glob.glob('bands/**/[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9].md',
                             recursive=True))
    if not files:
        print("❌ ERROR: No DD-MM-YYYY.md optimization files found!")
        print("   Expected structure: bands/[Letter]/[Artist]/[Song]/[ID]/DD-MM-YYYY.md")
        sys.exit(1)

    lf_o, sf_o = [], []
    lfd1, sfd1 = [], []
    lfp, sfp, gears = [], [], []

    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            t = fh.read()

        parts = t.split('## 2. SHORTS', 1)
        lf = parts[0]
        sf = parts[1] if len(parts) > 1 else ''

        lft, sft = g('Title', lf), g('Title', sf)
        lfd, sfd = g('Description', lf), g('Description', sf)
        lfp_val, sfp_val = g('Pinned Comment', lf), g('Pinned Comment', sf)

        for title, bucket in ((lft, lf_o), (sft, sf_o)):
            if title and not title.startswith('N/A'):
                match = re.match(r'([A-Za-z0-9][A-Za-z0-9!?\-\']*)', title)
                if match:
                    bucket.append(match.group(1).lower())

        if lfd and not lfd.startswith('N/A'):
            lfd1.append(lfd.splitlines()[0].strip())
        if sfd and not sfd.startswith('N/A'):
            sfd1.append(sfd.splitlines()[0].strip())

        if lfp_val and not lfp_val.startswith('N/A'):
            lfp.append(lfp_val)
        if sfp_val and not sfp_val.startswith('N/A'):
            sfp.append(sfp_val)

        gm = re.search(r'\*\*Genres:\*\*[^\n]*\n([^\n]*(?:Thunderbird|Rocksmith)[^\n]*)', lf)
        if gm:
            gears.append(gm.group(1).strip())

        # ---- VER 3.0: Folder Location must equal the real path ----
        m = re.search(r'\*\*Folder Location:\*\*\s*`([^`]+)`', t)
        real = os.path.dirname(f).replace(os.sep, '/') + '/'
        if not m:
            fail(f'{f}: missing **Folder Location:** line')
        elif m.group(1) != real:
            fail(f'{f}: Folder Location "{m.group(1)}" != actual "{real}"')

    print(f"Total optimization files found: {len(files)}")
    print()
    audit('Long-form title openers', lf_o)
    audit('Shorts title openers', sf_o)
    audit('Long-form desc first line', lfd1)
    audit('Shorts desc first line', sfd1)
    audit('Long-form pinned comments', lfp)
    audit('Shorts pinned comments', sfp)
    audit('Gear lines', gears)

    print()
    print("=" * 50)
    print("Section 1 Letter Convention")
    print("=" * 50)
    print()
    bad_letter = []
    for d in sorted(glob.glob('bands/*/*')):
        parts = d.split(os.sep)
        if len(parts) != 3:
            continue
        letter, artist = parts[1], parts[2]
        want = expected_letter(artist)
        if letter != want:
            bad_letter.append(f'{d} -> expected bands/{want}/{artist}')
    if bad_letter:
        for b in bad_letter:
            print(f'❌ {b}')
            fail(f'letter convention: {b}')
    else:
        print(f'✓ {len(glob.glob("bands/*/*"))} artist folders correctly lettered')

    print()
    print("=" * 50)
    print("Section 9 Tidy-Root Compliance Check")
    print("=" * 50)
    print()

    py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    if py_files:
        print(f"❌ FAIL: .py files found in root: {py_files}")
        fail(f'.py files in root: {py_files}')
    else:
        print("✓ No .py files in root directory")

    img_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    img_files = [f for f in os.listdir('.') if f.lower().endswith(img_exts)]
    if img_files:
        print(f"❌ FAIL: Image files found in root: {img_files}")
        fail(f'images in root: {img_files}')
    else:
        print("✓ No image files in root directory")

    print()
    print("=" * 50)
    if FAILS:
        print(f"❌ TIER-1 GATE FAILED — {len(FAILS)} violation(s):")
        for i, msg in enumerate(FAILS, 1):
            print(f"  {i:2d}. {msg}")
        sys.exit(1)
    print("✓ Tier-1 gate PASS — uniqueness, folder paths, lettering, tidy root")
    print("Verification complete!")
    sys.exit(0)


if __name__ == '__main__':
    main()
