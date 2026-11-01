================================================================================
MAVOmusic (@mavomusicyt) - PER-CHAT ATTACHMENT KIT - VER 3.0 (2026-11-01)
================================================================================
Paste the CONTENTS of this folder at the start of every new chat. The platform
accepts TEXT FILES ONLY (images excepted) - .py/.md/.xlsx/.zip cannot be pasted,
which is why every script and package is serialized inside the Recovery_*.txt
containers below. NEW CHATS NEED NO ZIP - the kit is the portable state source.

VER 3.0 NOTE: the workspace now also lives in the GitHub repo
MAVOmusic/YouTube-SEO (Test Image.jpg + frozen Ver 2.68/ + active Ver 3.0/).
If the chat has repo access, the kit is redundant but harmless - repo access is
faster and the kit is the fallback when it is not available.

RESTORE ORDER (VER 3.0):
  0. VISION SELF-CHECK FIRST (00_VISION_CHECK_FIRST.txt / CONTEXT §28).
     Confirm the chat can read images. If NO vision -> STOP and tell MAVO plainly.
  1. Read 01_CONTEXT_BLOCK.txt            -> ruleset + VER 3.0 layout (§29) + gate (§30)
  2. Read 07_MAVO_VERSION_LOG.txt         -> project state (Ver 1.02 -> 3.0)
  3. Decode 02_Recovery_Scripts.txt       -> PY/*.py (11 tools) + requirements.txt + verify.sh
  4. pip install -r PY/requirements.txt   -> openpyxl (the only dependency; XLSX needs it)
  5. Decode 03-06_Recovery_Data_a-d.txt   -> bands/ (308 packages, 77/77/77/77)
  6. Run the CONTEXT §29 cascade, ending with bash verify.sh -> ALL GATES GREEN ✓
       python3 PY/generate_track_history.py
       python3 PY/generate_reference_txts.py
       python3 PY/build_master_under_review.py
       python3 PY/repack.py
       python3 PY/refresh_kit.py
       bash verify.sh
  7. Read the analytics/reference files before touching tags, analytics or flags.

VER 3.0 TOOLCHAIN FACTS (know these before you debug anything):
  - Every tool is ROOT-PORTABLE: $MAVO_ROOT, else the folder two levels above the
    script. No /home/user edits, ever. verify.sh finds its own folder.
  - bash verify.sh EXITS 1 on any violation (it could not fail before VER 3.0).
  - recover_mavo.py is SUPERSEDED - never run it; the base64 containers are the
    only restore path.
  - PY/refresh_kit.py rebuilds this kit and byte-verifies all 23 copies.

FILE MANIFEST (kit files 00-23):
  00_PASTE_PRIORITY.txt ................ paste triage and restore order
  00_VISION_CHECK_FIRST.txt ............ step-0 vision gate
  01_CONTEXT_BLOCK.txt ................. master ruleset (VER 3.0 ACTIVE)
  02_Recovery_Scripts.txt ............. base64: 11 PY tools + requirements.txt + verify.sh
  03_Recovery_Data_a.txt ............... base64: packages 001-077
  04_Recovery_Data_b.txt ............... base64: packages 078-154
  05_Recovery_Data_c.txt ............... base64: packages 155-231
  06_Recovery_Data_d.txt ............... base64: packages 232-308
  07_MAVO_VERSION_LOG.txt ............. per-version audit narratives (Ver 1.02-3.0)
  08_README_FIRST.txt ................. this file
  09_Analytics_Of_Songs_0001_0050.txt . Studio screenshot extractions 0001-0050 (CLOSED)
  10_Analytics_Of_Songs_0051_0100.txt . songs 0051-0100 (filed through 0069)
  11_Analytics_Of_Songs_0101_0150.txt . songs 0101-0150 (open)
  12_Matched_Shorts_To_Cross_Check.txt  154 matched alternate cuts <-> canonical targets
  13_Master_Long_Form_Repository_0001_0702.txt
  14_Master_Shorts_Repository.txt ..... 2,460 Shorts rows (source of truth)
  15_Backlog_Duplicate_Shorts_Audit_0151_2460.txt ... duplicate-cluster velocity data
  16_Master_Under_Review_Audit.txt .... THE cleaned Under Review master
  17_Shorts_ID_Whitelist_0133_2460.txt  approved Shorts IDs (plain 4-digit)
  18_MAVO_PROJECT_LOG.txt ............. long-form project history + carry-over
  19_Pipeline_Notes_2026-08.txt ....... 0151+ re-record, lyrics format, SEO backlog
  20_Blocked_Claims_Register.txt ...... blocked-claims register
  21_Repurposing_0051_0100.txt ........ live tier boards
  22_Repurposing_0001_0050.txt ........ closed tier boards
  23_Analytics_Of_Songs_0151_0200.txt . 0151+ screenshot analytics extension
  24_Channel_Order_Audit_Log.txt ...... CO-NNNN upload-order audits (§31; opened VER 3.1)

CURRENT STATUS (VER 3.0):
  - 308 SEO packages; 308-record history (CSV + XLSX in sync); diversity gate
    0 violations / 0 warnings; Tier-1 gate green with the new hard contract.
  - Recheck queue remains parked at 0070 for the older 0070-0083 panel backlog.
  - Songs 0151-0154 have complete LF+SF Studio audits and new packages:
    0151 Kiss, 0152 The Vines, 0153 Brian Adam McCune, 0154 Good Charlotte.
    Their panel images are retained at IMAGES/Inherited_0151-0154_Panels/.
  - Wikipedia song-page genres used where explicitly available: 0151 Hard rock /
    arena rock, 0152 Garage rock, 0153 Christmas carol. For 0154, no dedicated
    song genre is listed; album-level Pop-punk/emo is labelled only as context.
  - From 0151 onward, the re-record programme builds a new LF and updated SF beside
    legacy Shorts. Do not delete/re-upload legacy Shorts unless the documented
    exception applies.
  - OUTSTANDING: paste the new 0085 Shorts title in Studio if 0085S is live.

These are COPIES; canonical homes: workspace root, TXT/, Under Review/, Whitelist/.
Refresh them with: python3 PY/refresh_kit.py
================================================================================
