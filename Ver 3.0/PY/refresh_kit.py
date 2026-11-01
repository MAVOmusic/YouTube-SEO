#!/usr/bin/env python3
"""
MAVOmusic Per-Chat Attachment Kit refresher (VER 3.0 - new)
===========================================================
Section 24 kit-refresh convention (v1.91) was a manual copy job every version,
which is exactly how kit drift happens. This automates it:

  canonical source                      ->  To Attach/NN_<name>.txt
  CONTEXT_BLOCK.txt                     ->  01_CONTEXT_BLOCK.txt
  TXT/Recovery_Scripts.txt              ->  02_Recovery_Scripts.txt
  TXT/Recovery_Data_a..d.txt            ->  03..06_Recovery_Data_x.txt
  MAVO_VERSION_LOG.txt                  ->  07_MAVO_VERSION_LOG.txt
  TXT/README_FIRST.txt                  ->  08_README_FIRST.txt
  TXT/Analytics_Of_Songs_*.txt          ->  09/10/11/23_*.txt
  Matched_Shorts_To_Cross_Check.txt     ->  12_Matched_Shorts_To_Cross_Check.txt
  TXT/Master_Long_Form_Repository_*.txt ->  13_*.txt
  TXT/Master_Shorts_Repository.txt      ->  14_*.txt
  TXT/Backlog_Duplicate_Shorts_*.txt    ->  15_*.txt
  Under Review/Master_Under_Review_*.txt->  16_*.txt
  Whitelist/Shorts_ID_Whitelist_*.txt   ->  17_*.txt
  MAVO_PROJECT_LOG.txt                  ->  18_MAVO_PROJECT_LOG.txt
  TXT/Pipeline_Notes_2026-08.txt        ->  19_*.txt
  TXT/Blocked_Claims_Register.txt       ->  20_*.txt
  TXT/Repurposing_0051_0100.txt         ->  21_*.txt
  TXT/Repurposing_0001_0050.txt         ->  22_*.txt

00_PASTE_PRIORITY.txt and 00_VISION_CHECK_FIRST.txt are AUTHORED files (not
copies) - they are never overwritten, only reported if missing.

Run AFTER repack.py (the kit ships the fresh Recovery containers):
    python3 PY/repack.py && python3 PY/refresh_kit.py
Exit 0 = every kit file byte-identical to its canonical source.
"""

import os
import shutil
import sys

ROOT = os.environ.get('MAVO_ROOT') or os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, 'To Attach')

MAP = [
    ('01_CONTEXT_BLOCK.txt', 'CONTEXT_BLOCK.txt'),
    ('02_Recovery_Scripts.txt', 'TXT/Recovery_Scripts.txt'),
    ('03_Recovery_Data_a.txt', 'TXT/Recovery_Data_a.txt'),
    ('04_Recovery_Data_b.txt', 'TXT/Recovery_Data_b.txt'),
    ('05_Recovery_Data_c.txt', 'TXT/Recovery_Data_c.txt'),
    ('06_Recovery_Data_d.txt', 'TXT/Recovery_Data_d.txt'),
    ('07_MAVO_VERSION_LOG.txt', 'MAVO_VERSION_LOG.txt'),
    ('08_README_FIRST.txt', 'TXT/README_FIRST.txt'),
    ('09_Analytics_Of_Songs_0001_0050.txt', 'TXT/Analytics_Of_Songs_0001_0050.txt'),
    ('10_Analytics_Of_Songs_0051_0100.txt', 'TXT/Analytics_Of_Songs_0051_0100.txt'),
    ('11_Analytics_Of_Songs_0101_0150.txt', 'TXT/Analytics_Of_Songs_0101_0150.txt'),
    ('12_Matched_Shorts_To_Cross_Check.txt', 'Matched_Shorts_To_Cross_Check.txt'),
    ('13_Master_Long_Form_Repository_0001_0702.txt',
     'TXT/Master_Long_Form_Repository_0001_0702.txt'),
    ('14_Master_Shorts_Repository.txt', 'TXT/Master_Shorts_Repository.txt'),
    ('15_Backlog_Duplicate_Shorts_Audit_0151_2460.txt',
     'TXT/Backlog_Duplicate_Shorts_Audit_0151_2460.txt'),
    ('16_Master_Under_Review_Audit.txt', 'Under Review/Master_Under_Review_Audit.txt'),
    ('17_Shorts_ID_Whitelist_0133_2460.txt',
     'Whitelist/Shorts_ID_Whitelist_0133_2460.txt'),
    ('18_MAVO_PROJECT_LOG.txt', 'MAVO_PROJECT_LOG.txt'),
    ('19_Pipeline_Notes_2026-08.txt', 'TXT/Pipeline_Notes_2026-08.txt'),
    ('20_Blocked_Claims_Register.txt', 'TXT/Blocked_Claims_Register.txt'),
    ('21_Repurposing_0051_0100.txt', 'TXT/Repurposing_0051_0100.txt'),
    ('22_Repurposing_0001_0050.txt', 'TXT/Repurposing_0001_0050.txt'),
    ('23_Analytics_Of_Songs_0151_0200.txt', 'TXT/Analytics_Of_Songs_0151_0200.txt'),
    ('24_Channel_Order_Audit_Log.txt', 'TXT/Channel_Order_Audit_Log.txt'),
    ('25_Channel_Analytics_Store.txt', 'TXT/Channel_Analytics_Store.txt'),
]

AUTHORED = ['00_PASTE_PRIORITY.txt', '00_VISION_CHECK_FIRST.txt']


def main():
    os.makedirs(KIT, exist_ok=True)
    bad = []
    for kit_name, rel in MAP:
        src = os.path.join(ROOT, rel)
        dst = os.path.join(KIT, kit_name)
        if not os.path.exists(src):
            bad.append(f'MISSING SOURCE: {rel} (needed for {kit_name})')
            continue
        shutil.copyfile(src, dst)
        if open(src, 'rb').read() != open(dst, 'rb').read():
            bad.append(f'COPY MISMATCH: {kit_name}')
    for name in AUTHORED:
        if not os.path.exists(os.path.join(KIT, name)):
            bad.append(f'MISSING AUTHORED FILE: To Attach/{name}')

    print(f'kit refreshed: {len(MAP)} copies -> To Attach/')
    if bad:
        for b in bad:
            print('❌', b)
        sys.exit(1)
    print('KIT SYNC PERFECT - every file byte-identical to its canonical source')
    sys.exit(0)


if __name__ == '__main__':
    main()
