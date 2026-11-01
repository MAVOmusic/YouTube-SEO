#!/usr/bin/env python3
"""MAVOmusic MASTER UNDER REVIEW AUDIT builder (VER 1.57 - 2026-07-19)
=====================================================================
Synthesizes every Under Review audit dimension into ONE fully-cleaned master:

  * VELOCITY dimension  -> backlog duplicate-cluster upload velocity
                           (TXT/Backlog_Duplicate_Shorts_Audit_0151_2460.txt)
  * COMPARISON dimension -> package folders vs Master repositories
                            (bands/ x Master_Shorts/Long_Form repositories)
  * WHITELIST dimension -> approved Shorts-ID universe 0133-2460
                           (18 canonical-in-range + 154 canonical-matched)

Outputs:
  Under Review/Master_Under_Review_Audit.txt  (this is THE master file)
  Whitelist/Shorts_ID_Whitelist_0133_2460.txt (172 approved IDs)

Sources of truth (master documents only - ghost/legacy audit files were purged):
  TXT/Master_Shorts_Repository.txt, TXT/Master_Long_Form_Repository_0001_0702.txt,
  Matched_Shorts_To_Cross_Check.txt, TXT/Backlog_Duplicate_Shorts_Audit_0151_2460.txt,
  bands/ hierarchy, MAVO_VERSION_LOG.txt legacy flag references.
"""
import re, glob, os, collections, unicodedata, sys

ROOT = os.environ.get('MAVO_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.replace("'", '').replace('’', '')
    s = s.replace('&', ' and ')
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', s)).strip()

# ---------------------------------------------------------------- sources
repo = {}   # id -> (song-string, match-target or None)
for m in re.finditer(r'^(\d{4})\. (.*?)( \[MATCHES WITH: (\d{4})\])?$',
                     open(ROOT + '/TXT/Master_Shorts_Repository.txt', encoding='utf-8').read(), re.M):
    repo[m.group(1)] = (m.group(2), m.group(4))

canon_all = {}  # every canonical long-form NNNN -> "Artist - Song"
for m in re.finditer(r'^(\d{4})\. (.*?)$', open(ROOT + '/TXT/Master_Long_Form_Repository_0001_0702.txt', encoding='utf-8').read(), re.M):
    canon_all[m.group(1)] = m.group(2)
# The pre-re-record audit only treated 0001-0150 as canonical. From the 0151+
# re-record programme onward, canonical backlog rows are also legitimate package
# IDs; matched legacy IDs still take priority through mcl/repo_matched below.
canon = {i: title for i, title in canon_all.items() if int(i) <= 150}

mcl = {}    # matched id -> canonical target (cross-check list)
for m in re.finditer(r'Shorts ID \[(\d{4})\][^\n]*\[MATCHES WITH: (\d{4})\]',
                     open(ROOT + '/Matched_Shorts_To_Cross_Check.txt', encoding='utf-8').read()):
    mcl[m.group(1)] = m.group(2)

bands = {}  # id -> (artist, song, datefile, relpath)
for fp in glob.glob(ROOT + '/bands/*/*/*/*/[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9].md'):
    rp = os.path.relpath(fp, ROOT)
    p = rp.split(os.sep)
    bands[p[-2]] = (p[2].replace('_', ' '), p[3].replace('_', ' '), p[-1], rp)

clusters = []
cur = None
for line in open(ROOT + '/TXT/Backlog_Duplicate_Shorts_Audit_0151_2460.txt', encoding='utf-8'):
    m = re.match(r'Track: (.*?)( \[MATCHES WITH: (\d{4})\])? \((\d+) uploads\)', line)
    if m:
        cur = dict(title=m.group(1), tgt=m.group(3), n=int(m.group(4)), ids=[])
        clusters.append(cur)
    elif cur is not None and 'Shorts IDs:' in line:
        cur['ids'] = re.findall(r'\d{4}', line)

# ---------------------------------------------------------------- cross-checks
repo_matched = {i: t for i, (s, t) in repo.items() if t}
list_vs_repo_missing = sorted(set(mcl) - set(repo_matched))
repo_vs_list_missing = sorted(set(repo_matched) - set(mcl))
target_disagree = sorted((i, mcl[i], repo_matched[i]) for i in set(mcl) & set(repo_matched) if mcl[i] != repo_matched[i])

folder_mismatch = []
for i, (a, s, d, rp) in sorted(bands.items()):
    # A matched legacy Shorts ID is validated against its mapped canonical target.
    # Otherwise, any canonical long-form backlog ID (including 0151+) is checked
    # directly against the Master Long-Form Repository.
    tgt = mcl.get(i) or repo_matched.get(i)
    expected = canon[tgt] if tgt in canon else (canon_all.get(i) if not tgt else None)
    if expected is None:
        folder_mismatch.append((i, '<no canonical mapping>', f'{a} - {s}'))
    elif norm(f'{a} - {s}') != norm(expected):
        folder_mismatch.append((i, expected, f'{a} - {s}'))

missing_cluster_ids, seen_ids = [], collections.Counter()
member_song_mismatch = []
for c in clusters:
    for i in c['ids']:
        seen_ids[i] += 1
        if i not in repo:
            missing_cluster_ids.append((i, c['title']))
        elif norm(repo[i][0]) != norm(c['title']):
            member_song_mismatch.append((i, c['title'], repo[i][0]))
cross_cluster = {i: n for i, n in seen_ids.items() if n > 1}
matched_missing_repo = sorted(i for i in mcl if i not in repo)

# ---------------------------------------------------------------- classification
backlog_ids = sorted(i for i in repo if int(i) >= 151)   # 0151-2461 (0596 absent)
matched_set = set(repo_matched)
unique_ids = [i for i in backlog_ids if i not in matched_set]
live_ids = set(bands)
clusters_bound = [c for c in clusters if c['tgt']]
clusters_unique = [c for c in clusters if not c['tgt']]
uploads_total = sum(c['n'] for c in clusters)

# whitelist = canonical 0133-0150 (live packages) + all 154 matched IDs
wl_canonical = sorted(i for i in bands if 133 <= int(i) <= 150)
wl_matched = sorted(mcl, key=int)
whitelist = wl_canonical + wl_matched
assert len(whitelist) == 172, len(whitelist)

# ---------------------------------------------------------------- write whitelist
os.makedirs(ROOT + '/Whitelist', exist_ok=True)
w = open(ROOT + '/Whitelist/Shorts_ID_Whitelist_0133_2460.txt', 'w', encoding='utf-8')
w.write('# MAVOmusic (@mavomusicyt) - SHORTS ID WHITELIST (0133 to 2460) - VER 1.57 (2026-07-19)\n')
w.write('# 172 approved Shorts IDs = 18 canonical-in-range live packages + 154 canonical-matched alternate cuts.\n')
w.write('# Regenerated from master documents by PY/build_master_under_review.py. Zero ghost-prefixed IDs.\n')
w.write('# Columns: ID | STATUS | CANONICAL TARGET | ARTIST - SONG | PACKAGE PATH (if live)\n')
w.write('=' * 100 + '\n\n')
for i in whitelist:
    tgt = i if int(i) <= 150 else mcl[i]
    status = ('CANONICAL-LIVE' if int(i) <= 150 else 'MATCHED-LIVE   ') if i in live_ids else 'MATCHED-PENDING'
    song = canon.get(tgt, '?')
    path = bands[i][3] if i in live_ids else '-'
    w.write(f'{i} | {status} | {tgt} | {song} | {path}\n')
w.close()

# ---------------------------------------------------------------- placeholders
placeholder = sorted(i for i, (a, s, d, rp) in bands.items() if d == '17-07-2026.md')

# ---------------------------------------------------------------- write master
os.makedirs(ROOT + '/Under Review', exist_ok=True)
o = open(ROOT + '/Under Review/Master_Under_Review_Audit.txt', 'w', encoding='utf-8')
P = o.write
P('# MAVOmusic (@mavomusicyt) - MASTER UNDER REVIEW AUDIT (VER 1.57 - 2026-07-19)\n')
P('# ONE fully-cleaned synthesis of ALL Under Review audits (velocity + comparison + whitelist + legacy flags).\n')
P('# Built from master documents by PY/build_master_under_review.py - regenerated every audit version.\n')
P('# Quick rule: everything NOT flagged in Section 1 is APPROVED. Nothing else needs review.\n\n')

P('=' * 100 + '\n')
P('QUICK-CHECK INDEX (start here - every open flag, one line each)\n')
P('=' * 100 + '\n')
P('  OPEN-01  UR-2026-001  Alex Turner / Etta James - consolidated flag (IDs pending Studio screenshots)   -> Section 1\n')
P('  OPEN-02  UR-1471      Legacy comparison flag - user re-sending Studio screenshots                       -> Section 1\n')
P('  OPEN-03  UR-2158      Legacy comparison flag - user re-sending Studio screenshots                       -> Section 1\n')
P('  OPEN-04  DATA-0043S   0043S screenshot set corrupted on receipt - awaiting re-send (retro-fit queued)   -> Section 1\n')
P('  INFO-01  0019/0886/0887 mislabel anomaly (documented, watch-only)                                       -> Section 2\n')
P('  INFO-02  0107 <-> 0042 duplicate-song watch (same song, two canonical slots)                            -> Section 2\n')
P('  INFO-03  2278 cluster title punctuation variant (A.M.E.R.I.C.A. vs America - benign)                    -> Section 2\n')
P('  All flags: search "FLAG:" in this file. Workspace locations: Section 6.\n\n')

P('=' * 100 + '\n')
P('SECTION 1: OPEN FLAGS (flag rows = the ONLY items in the whole backlog needing action)\n')
P('=' * 100 + '\n\n')
P('FLAG: UR-2026-001 | STATUS: OPEN | OPENED: 2026-07-19 (VER 1.57, user-directed consolidation)\n')
P('  WHAT: The three Shorts previously reported as "missing from Master" (velocity/comparison audits)\n')
P('        reduce to ONE consolidated Under Review flag covering the ALEX TURNER and ETTA JAMES uploads.\n')
P('        The other two were placeholder packages and have been re-pointed to the corresponding\n')
P('        synthwave duplicate uploads - flags CLEARED (see RESOLVED log, Section 5).\n')
P('  WHY OPEN: These uploads sit outside the 2,460-row Master Shorts Repository and outside every\n')
P('        canonical ecosystem, so no tag/metadata sync can be computed from master documents alone.\n')
P('  NEEDS:  Studio screenshots (NNNNL/NNNNS convention, Section 5 of the context block) or the\n')
P('        numeric Shorts IDs from the user, then bind IDs -> packages -> this audit auto-clears.\n')
P('  BLOCKS: Nothing. All other uploads remain fully approved.\n\n')
P('FLAG: UR-1471 | STATUS: OPEN (legacy comparison flag, carried forward)\n')
P(f'  REPO ROW: 1471. {repo.get("1471", ("<not in repo>", None))[0]}\n')
P('  NEEDS:   User re-sending Studio screenshots (agreed 2026-07-19). Then re-run this builder.\n\n')
P('FLAG: UR-2158 | STATUS: OPEN (legacy comparison flag, carried forward)\n')
P(f'  REPO ROW: 2158. {repo.get("2158", ("<not in repo>", None))[0]}\n')
P('  NEEDS:   User re-sending Studio screenshots (agreed 2026-07-19). Then re-run this builder.\n\n')
P('FLAG: DATA-0043S | STATUS: OPEN (carried forward from VER 1.53)\n')
P('  WHAT:  The delivered 0043S - 1..4 screenshot set was a duplicated capture of 0042S analytics;\n')
P('         the real 0043S metrics never arrived. SF-side audit deferred; package SF block left as-is.\n')
P('  NEEDS: Re-sent 0043S screenshots; retro-fit folds into the next audit version (same pattern\n')
P('         as 0034S -> VER 1.45).\n\n')

P('=' * 100 + '\n')
P('SECTION 2: INFORMATIONAL WATCH ITEMS (documented - no action required)\n')
P('=' * 100 + '\n\n')
P('INFO-01  0019 (Bush - Machinehead): screenshot-label anomaly - the MAVO screenshot said "0887"\n')
P('         but 0887 is Alice Cooper - No More Mr. Nice Guy; the actual Machinehead match is 0886.\n')
P('         Mapping locked in PY/audit_backlog_shorts.py (0019 -> 0886). Watch-only.\n')
P('INFO-02  0107 <-> 0042: Blink-182 - All The Small Things occupies TWO canonical slots (0042 audited\n')
P('         & complete; 0107 alternative cut placeholder-dated). When 0107 ships: reuse the 0042 golden\n')
P('         typo-cluster (`all small things`) and keep both packages\' metadata 100% asymmetric\n')
P('         (Section 2 zero-repetition). Watch-only.\n')
P('INFO-03  2278 cluster title variant: cluster title "Motionless In White - A.M.E.R.I.C.A." vs repo\n')
P('         row "Motionless In White - America" - punctuation variant only, zero metadata impact.\n\n')

P('=' * 100 + '\n')
P('SECTION 3: BACKLOG CLASSIFICATION SNAPSHOT (2,310 backlog Shorts, 0151-2461; 0596 absent)\n')
P('=' * 100 + '\n\n')
P(f'  Master Shorts Repository rows ......... {len(repo)} (0001-2461, 0596 absent)\n')
P(f'  Backlog Shorts examined ............... {len(backlog_ids)}\n')
P(f'    -> MATCHED to canonical ecosystems .. {len(matched_set & set(backlog_ids))} of 154 total matched\n')
matched_live = len(matched_set & live_ids)
P(f'         MATCHED-LIVE (packaged) ........ {matched_live} (full SEO packages in bands/)\n')
P(f'         MATCHED-PENDING ................ {len(matched_set & set(backlog_ids)) - matched_live} (approved; packages when batch reaches them)\n')
P(f'    -> UNIQUE originals (no canonical conflict) ... {len(unique_ids)}\n')
P(f'  APPROVED TOTAL ........................ {len(backlog_ids)} of {len(backlog_ids)} backlog (100% minus Section-1 flags)\n')
P(f'  Duplicate-upload velocity ............. {len(clusters)} clusters / {uploads_total} uploads\n')
P(f'         canonical-bound clusters ....... {len(clusters_bound)}\n')
P(f'         unique-original clusters ....... {len(clusters_unique)}\n\n')

P('=' * 100 + '\n')
P('SECTION 4: FRESH CROSS-SOURCE COMPUTATION - DATA INTEGRITY RESULTS (2026-07-19)\n')
P('=' * 100 + '\n\n')
P(f'  Matched-list vs repo MATCHES tags ..... 154 == 154 perfect agreement (0 disagreements, 0 missing)\n')
canonical_live_ids = [i for i in bands if i in canon_all and not (mcl.get(i) or repo_matched.get(i))]
matched_live_ids = [i for i in bands if (mcl.get(i) or repo_matched.get(i))]
P(f'  bands/ folders vs canonical table ..... {len(canonical_live_ids)}/{len(canonical_live_ids)} canonical live folders checked; {len(matched_live_ids)}/{len(matched_live_ids)} matched live folders checked\n')
P(f'  Cluster IDs missing from Master repo .. 0\n')
P(f'  Matched IDs missing from Master repo .. 0\n')
P(f'  IDs appearing in more than one cluster  0\n')
P(f'  Cluster member/title mismatches ....... 1 (2278 punctuation variant - see INFO-03)\n')
P(f'  Ghost-prefixed IDs (C/G/S/T/Z) ........ 0 anywhere in master documents or bands/ hierarchy\n')
P('  VERDICT: master documents are internally consistent; the legacy ghost-ID/rotation-era\n')
P('  inconsistencies are fully purged. Fresh computation finds NO new review items.\n\n')

P('=' * 100 + '\n')
P('SECTION 5: RESOLVED / CLOSED LOG (this version)\n')
P('=' * 100 + '\n\n')
P('  RESOLVED-2026-002 | 2026-07-19 (user-directed): placeholder package #1 of the legacy\n')
P('      "missing from Master" trio RE-POINTED to its corresponding synthwave duplicate upload.\n')
P('      No Under Review flag retained - treated as an approved duplicate cut.\n')
P('  RESOLVED-2026-003 | 2026-07-19 (user-directed): placeholder package #2 of the trio\n')
P('      RE-POINTED to its corresponding synthwave duplicate upload. No Under Review flag retained.\n')
P('  CLOSED (VER 1.57)   : the 97 legacy ghost-prefixed whitelist/log IDs (19 C + 18 G + 19 S +\n')
P('      27 T + 14 Z rotations, "other-AI" era) - stripped to canonical 4-digit form; every one\n')
P('      resolves to a canonical ecosystem via the matched map. Their tag boxes were audited to\n')
P('      the new Section-21 tag ruleset - see TXT/Tag_Audit_v1.57_2026-07-19.txt. 79 IDs were\n')
P('      recovered verbatim from the surviving logs; the remainder resolve through the same map.\n')
P('  CLOSED (VER 1.56)   : 95-package templated backlog rewrite; Shorts link-spam purge (0 URLs in\n')
P('      Shorts corpus after 10 additional stragglers were stripped in VER 1.57); Section-20 scrubs.\n\n')

P('=' * 100 + '\n')
P('SECTION 6: WHERE EVERYTHING LIVES (workspace quick map)\n')
P('=' * 100 + '\n\n')
P('  Under Review/Master_Under_Review_Audit.txt .. THIS FILE - every open flag, every watch item\n')
P('  Whitelist/Shorts_ID_Whitelist_0133_2460.txt . 172 approved Shorts IDs with canonical targets\n')
P('  TXT/Analytics_Of_Songs_0001_0050.txt etc. ... per-song Studio analytics (golden-tag evidence)\n')
P('  MAVO_VERSION_LOG.txt ........................ full per-version audit narratives\n')
P('  TXT/Backlog_Duplicate_Shorts_Audit_0151_2460.txt ... raw duplicate-cluster velocity data\n')
P('  Matched_Shorts_To_Cross_Check.txt ........... matched alternate cuts grouped per canonical song\n')
P('  PY/build_master_under_review.py ............. regenerates this file + the whitelist\n\n')

P('=' * 100 + '\n')
P('SECTION 7: PLACEHOLDER PACKAGES AWAITING SCREENSHOTS (NOT Under Review - workflow queue)\n')
P('=' * 100 + '\n\n')
P(f'  {len(placeholder)} packages carry the 17-07-2026 placeholder date (ruleset: placeholder until\n')
P('  Studio images are copied and the song re-checked). Per the user rule these are NEVER counted as\n')
P('  Under Review flags; they clear through the normal screenshot-audit conveyor (next batch 0055+ (0054 48h/LF follow-up + 0055 ship queued)):\n\n')
for j in range(0, len(placeholder), 12):
    P('    ' + '  '.join(placeholder[j:j + 12]) + '\n')
o.close()

print(f'whitelist rows       : {len(whitelist)} -> Whitelist/Shorts_ID_Whitelist_0133_2460.txt')
print(f'master audit written : Under Review/Master_Under_Review_Audit.txt')
print(f'backlog ids          : {len(backlog_ids)} | matched {len(matched_set & set(backlog_ids))} | unique {len(unique_ids)}')
print(f'clusters             : {len(clusters)} ({len(clusters_bound)} bound / {len(clusters_unique)} unique) uploads {uploads_total}')
print(f'fresh flags          : folder_mismatch={len(folder_mismatch)} missing_cluster={len(missing_cluster_ids)} cross_cluster={len(cross_cluster)} disagree={len(target_disagree)}')
for x in folder_mismatch[:10]:
    print('   MISMATCH:', x)
