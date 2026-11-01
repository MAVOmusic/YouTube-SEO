#!/usr/bin/env python3
"""MAVOmusic Reference TXT Regenerator (v1.57)
=====================================================
Rebuilds TXT/Titles.txt, TXT/Descriptions.txt, TXT/Pinned_Comments.txt and
TXT/Tags.txt from the live bands/ hierarchy using the Section-21 v1.2 parser
(correctly maps single-section "Matched Short" packages to their SHORTS box).

Layout per block:  [NNNN] bands/<path>/<DD-MM-YYYY>.md  then  LF:/SF: lines.
Run after any package edit so the cumulative reference files never drift.
"""
import glob, os, sys

ROOT = os.environ.get('MAVO_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'PY'))
from diversity_guard import get_fields  # noqa: E402

FILES = sorted(glob.glob(ROOT + '/bands/**/*.md', recursive=True))

def main():
    outs = {
        'title': open(ROOT + '/TXT/Titles.txt', 'w', encoding='utf-8'),
        'desc':  open(ROOT + '/TXT/Descriptions.txt', 'w', encoding='utf-8'),
        'pin':   open(ROOT + '/TXT/Pinned_Comments.txt', 'w', encoding='utf-8'),
        'tags':  open(ROOT + '/TXT/Tags.txt', 'w', encoding='utf-8'),
    }
    n = 0
    for fp in FILES:
        rel = os.path.relpath(fp, ROOT)
        id_folder = os.path.basename(os.path.dirname(fp))
        F = get_fields(open(fp, encoding='utf-8').read())
        header = f'[{id_folder}] {rel}\n'
        outs['title'].write(header + f"LF: {F['lf_title']}\nSF: {F['sf_title']}\n\n")
        outs['desc'].write(header + f"LF:\n{F['lf_desc']}\n\nSF:\n{F['sf_desc']}\n\n")
        outs['pin'].write(header + f"LF: {F['lf_pin']}\nSF: {F['sf_pin']}\n\n")
        outs['tags'].write(header + f"LF: {F['lf_tags']}\nSF: {F['sf_tags']}\n\n")
        n += 1
    for f in outs.values():
        f.close()
    print(f'reference TXT files regenerated for {n} packages -> TXT/')

if __name__ == '__main__':
    main()
