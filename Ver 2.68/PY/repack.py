#!/usr/bin/env python3
"""Re-serialize all recovery containers + round-trip verify."""
import base64, glob, os, sys, re

ROOT = '/home/user'
VER = 'VER 2.65 - 2026-08-07'

def container(path, title, files):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'# MAVOmusic Restoration Package - {title} ({VER})\n')
        f.write('# Decode each base64 block back to the file named in its FILE: header.\n\n')
        for rel in files:
            raw = open(os.path.join(ROOT, rel), 'rb').read()
            f.write(f'# ===== FILE: {rel} =====\n')
            f.write(base64.b64encode(raw).decode('ascii') + '\n\n')
        f.write(f'# Restored {len(files)} files. End of container.\n')

# scripts container: all tools + verify.sh
tools = sorted(os.path.relpath(p, ROOT) for p in glob.glob(ROOT + '/PY/*.py'))
tools.append('verify.sh')
container(ROOT + '/TXT/Recovery_Scripts.txt', 'Scripts & Tools', tools)

# data containers: dynamic 4-way split
mds = sorted(os.path.relpath(p, ROOT) for p in glob.glob(ROOT + '/bands/**/*.md', recursive=True))
NEED = len(mds)
base, extra = divmod(NEED, 4)
chunks, pos = [], 0
for j in range(4):
    n = base + (1 if j < extra else 0)
    chunks.append(mds[pos:pos + n]); pos += n
for name, chunk in zip('abcd', chunks):
    container(f'{ROOT}/TXT/Recovery_Data_{name}.txt', f'Package Data {name}', chunk)
print('containers:', len(tools), 'tools;', [len(c) for c in chunks], 'packages')

# ---------------- round-trip verify ----------------
errors = 0
for cont in ['Recovery_Scripts.txt'] + [f'Recovery_Data_{c}.txt' for c in 'abcd']:
    text = open(f'{ROOT}/TXT/{cont}', encoding='utf-8').read()
    blocks = 0
    for m in re.finditer(r'# ===== FILE: (.*?) =====\n([A-Za-z0-9+/=\n]+?)\n\n', text):
        rel, b64 = m.group(1), m.group(2).replace('\n', '')
        blocks += 1
        try:
            decoded = base64.b64decode(b64)
        except Exception as e:
            print('DECODE FAIL', cont, rel, e); errors += 1; continue
        live_path = os.path.join(ROOT, rel)
        live = open(live_path, 'rb').read() if os.path.exists(live_path) else None
        if live != decoded:
            print('MISMATCH', cont, rel); errors += 1
    print(f'{cont}: {blocks} blocks round-trip checked')
print('ROUND-TRIP', 'FAILED' if errors else 'PERFECT - byte-identical')
sys.exit(1 if errors else 0)
