#!/usr/bin/env python3
"""
MAVOmusic Workspace Verification Script (Python version)
Upgraded for Nested Song-Title Folder Structure & Date-Based Filenames
Run from /home/user with: python3 PY/verify.py
"""

import re
import glob
import collections
import os

def main():
    os.chdir('/home/user')
    
    print("=" * 50)
    print("MAVOmusic Workspace Verification (v8 Structure)")
    print("=" * 50)
    print()
    
    # Updated glob to find all DD-MM-YYYY.md files
    files = sorted(glob.glob('bands/**/[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9].md', recursive=True))
    
    if not files:
        print("❌ ERROR: No DD-MM-YYYY.md optimization files found!")
        print("   Current structure expected: bands/[Letter]/[Artist]/[Song]/[ID]/DD-MM-YYYY.md")
        return
    
    lf_o = []
    sf_o = []
    lfd1 = []
    sfd1 = []
    lfp = []
    sfp = []
    gears = []
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            t = fh.read()
        
        def g(lab, src):
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
        
        parts = t.split('## 2. SHORTS', 1)
        lf = parts[0]
        sf = parts[1] if len(parts) > 1 else ''
        
        lft = g('Title', lf)
        sft = g('Title', sf)
        lfd = g('Description', lf)
        sfd = g('Description', sf)
        lfp_val = g('Pinned Comment', lf)
        sfp_val = g('Pinned Comment', sf)
        
        if lft and lft != 'N/A' and not lft.startswith('N/A'):
            match = re.match(r'([A-Za-z0-9][A-Za-z0-9!?\-]*)', lft)
            if match: lf_o.append(match.group(1).lower())
        
        if sft and sft != 'N/A' and not sft.startswith('N/A'):
            match = re.match(r'([A-Za-z0-9][A-Za-z0-9!?\-]*)', sft)
            if match: sf_o.append(match.group(1).lower())
        
        if lfd and lfd != 'N/A':
            lfd1.append(lfd.splitlines()[0].strip())
        if sfd and sfd != 'N/A':
            sfd1.append(sfd.splitlines()[0].strip())
            
        if lfp_val and lfp_val != 'N/A': lfp.append(lfp_val)
        if sfp_val and sfp_val != 'N/A': sfp.append(sfp_val)
        
        gm = re.search(r'\*\*Genres:\*\*[^\n]*\n([^\n]*(?:Thunderbird|Rocksmith)[^\n]*)', lf)
        if gm: gears.append(gm.group(1).strip())
    
    def audit(n, items):
        d = [x for x, c in collections.Counter(items).items() if c > 1]
        status = "DUPES: " + str(d) if d else "all unique ✓"
        print(f'{n:35s}: {len(items):3d} -> {status}')
    
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
    print("Section 11 Compliance Check")
    print("=" * 50)
    print()
    
    py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    if py_files:
        print(f"❌ FAIL: .py files found in root: {py_files}")
    else:
        print("✓ No .py files in root directory")
    
    img_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    img_files = [f for f in os.listdir('.') if any(f.endswith(e) for e in img_exts)]
    if img_files:
        print(f"❌ FAIL: Image files found in root: {img_files}")
    else:
        print("✓ No image files in root directory")
    
    print()
    print("Verification complete!")

if __name__ == '__main__':
    main()
