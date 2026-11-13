#!/usr/bin/env python3
"""Build and audit the copy workbook. Run before every delivery."""
import pathlib, re, sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "Ver 3.0/TXT/Copy_Workbook_0001_0010_And_New_Uploads.xlsx"
# Workbook order rule (user, 2026-11-11): a song's rows are never split across
# the sheet. Every newly edited or newly uploaded song moves, as one group, to
# the bottom of the file, all its long forms first (ascending) then all its
# Shorts (ascending), older versions included alongside the new ones. Append
# each new edited/uploaded song to EDITED_GROUPS in delivery order.
EDITED_GROUPS = ["motionless in white - masterpiece", "paramore - misery business",
                 "sabaton - the lion from the north", "yellowcard - ocean avenue",
                 "linkin park - runaway", "avril lavigne - take me away",
                 "+44 - chapter xiii", "exodus - toxic waltz",
                 "dashboard confessional - hands down", "death cab for cutie - transatlanticism",
                 "linkin park - forgotten", "pat benatar - love is a battlefield",
                 "metallica - for whom the bell tolls", "mayday parade - jamie all over"]
CURRENT_PAIRS = {("LF", 733), ("LF", 734), ("SF", 2480), ("SF", 2481),
                 ("LF", 700), ("LF", 706), ("LF", 745), ("LF", 746), ("LF", 747), ("LF", 715),
                 ("SF", 2447), ("SF", 2453), ("SF", 2492), ("SF", 2493), ("SF", 2494), ("SF", 2462)}
SONGS = ["autumn leaves","another life","masterpiece","abigail","a-m-e-r-i-c-a","immaculate misconception","x-kid","welcome to the black parade","if i'd been the one"]

def block(t, *heads):
    for h in heads:
        m = re.search(rf"## {h}[^\n]*\n.*?```text\n(.*?)```", t, re.S)
        if m: return m.group(1).strip()
    return ""

def ident_of(name):
    return re.sub(r"\s*\[U - [^\]]+\]\s*$", "", re.sub(r"\s*\((Long|Short) Form\)\s*$", "", name[7:])).strip()

def song_key(ident):
    # Same song under variant artist spellings counts as one song:
    # "+44 (Plus 44) - Chapter XIII" and "+44 - Chapter XIII" are one group.
    return ident.lower().replace("+44 (plus 44)", "+44")

def in_scope_flags(fmt, num, name):
    m = re.search(r"U - (2026-11-\d\d)", name)
    new = bool(m and m.group(1) >= "2026-11-06")
    recent = (fmt == "LF" and 673 <= num <= 688) or (fmt == "SF" and (2420 <= num <= 2435 or num in (467, 725)))
    return new or recent or (fmt, num) in CURRENT_PAIRS or (fmt == "LF" and num <= 10)

def collect():
    # Two passes. Pass one decides which songs are in scope (LF 0001-0010,
    # uploads from 6 Nov 2026, and the recent batches). Pass two then takes
    # EVERY version of those songs, whenever it was uploaded. Scope by song,
    # never by which individual files happen to match: older variants of an
    # in-scope song were silently missed before this (rule 7c).
    found = []
    for fmt, root in [("LF", ROOT/"_All Songs/_0001 Long Form"), ("SF", ROOT/"_All Songs/_0002 Short Form")]:
        for p in root.rglob("_03 - Copy.md"):
            name = p.parent.name; num = int(name[:4])
            found.append((fmt, num, name, p))
    songs = {song_key(ident_of(name)) for fmt, num, name, p in found if in_scope_flags(fmt, num, name)}
    rows = []
    for fmt, num, name, p in found:
        ident = ident_of(name)
        if song_key(ident) not in songs: continue
        t = p.read_text(encoding="utf-8", errors="ignore")
        pin = block(t, "CREATOR COMMENT TO POST", "PINNED COMMENT", "CREATOR COMMENT")
        rows.append({"band": f"{fmt} {num:04} | {ident}", "fmt": fmt, "num": num,
                     "title": block(t, "TITLE"), "desc": block(t, "DESCRIPTION"), "pin": pin, "path": str(p)})
    rows = sorted({r["path"]: r for r in rows}.values(), key=lambda r: (r["band"].split("| ",1)[-1].lower(), r["fmt"], r["num"]))
    bottom = []
    for g in EDITED_GROUPS:
        grows = [r for r in rows if song_key(r["band"].split("| ", 1)[-1]) == g]
        bottom += sorted(grows, key=lambda r: (r["fmt"] != "LF", r["num"]))
    return [r for r in rows if r not in bottom] + bottom

def first3(s):
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()[:3])

def missing_copy():
    # Completeness guard: an uploaded folder for an in-scope song with
    # screenshots or a [U - date] marker but no _03 - Copy.md is a problem,
    # not a silent miss (rules 7b and 7c).
    errs = []
    songs = set()
    for root in (ROOT/"_All Songs/_0001 Long Form", ROOT/"_All Songs/_0002 Short Form"):
        for p in root.rglob("_03 - Copy.md"):
            fmt = "LF" if "_0001 Long Form" in str(p) else "SF"
            name = p.parent.name
            if in_scope_flags(fmt, int(name[:4]), name): songs.add(song_key(ident_of(name)))
    for root in (ROOT/"_All Songs/_0001 Long Form", ROOT/"_All Songs/_0002 Short Form"):
        for folder in root.rglob("*"):
            if not folder.is_dir() or not re.match(r"\d{4} - ", folder.name): continue
            m = re.search(r"U - (2026-11-\d\d)", folder.name)
            uploaded = bool(m and m.group(1) >= "2026-11-06") or (folder/"_01 - Main Info").exists()
            variant = song_key(ident_of(folder.name)) in songs or any(s in folder.name.lower() for s in SONGS)
            if uploaded and variant and not (folder/"_03 - Copy.md").exists():
                errs.append(f"Missing copy file: {folder.name}")
    return errs

def audit(rows):
    errs = missing_copy()
    def dup(key, label):
        seen = {}
        for r in rows:
            k = first3(r[key])
            if k and k in seen: errs.append(f"{label} starter repeated: '{k}' in {r['band']} and {seen[k]}")
            seen.setdefault(k, r["band"])
    dup("title", "Title"); dup("desc", "Description"); dup("pin", "Comment")
    # Same-song rule 7a: variants of one song must not share a first word
    groups = {}
    for r in rows:
        ident = r["band"].split("| ", 1)[-1].lower()
        groups.setdefault(ident, []).append(r)
    for ident, grows in groups.items():
        if len(grows) < 2: continue
        for key in ("title", "desc", "pin"):
            seen = {}
            for r in grows:
                w = re.sub(r"[^a-z0-9 ]", " ", r[key].lower()).split()
                first = w[0] if w else ""
                if first and first in seen:
                    errs.append(f"Same-song starter shared: '{first}' opens the {key} of {r['band']} and {seen[first]}")
                seen.setdefault(first, r["band"])
    emojis = {}
    for r in rows:
        if not r["title"]: errs.append(f"{r['band']}: missing title")
        if not r["desc"]: errs.append(f"{r['band']}: missing description")
        if not r["pin"]: errs.append(f"{r['band']}: missing creator comment")
        if r["fmt"] == "LF" and "play along" in r["title"].lower(): errs.append(f"{r['band']}: LF title says play along")
        words = re.sub(r"[^a-z0-9 ]", " ", r["title"].lower()).split()
        if "on" in words[:5] and "bass" in words[:5]: errs.append(f"{r['band']}: title opens with song-on-bass")
        p1 = (r["pin"].splitlines() or [""])[0]
        if r["fmt"] == "SF":
            if "related video" not in p1.lower(): errs.append(f"{r['band']}: SF comment does not open with related video pointer")
            if "related video" not in r["pin"].lower(): errs.append(f"{r['band']}: SF comment has no CTA pointer")
            for dom in ("kick.com", "twitch.tv", "discord.gg"):
                if dom not in r["desc"]: errs.append(f"{r['band']}: SF description missing {dom} CTA")
            e = p1.split(" ")[0]
            if e in emojis: errs.append(f"{r['band']}: SF comment opening emoji {e} already used by {emojis[e]}")
            emojis.setdefault(e, r["band"])
    return errs

def main():
    rows = collect()
    errs = audit(rows)
    wb = Workbook(); ws = wb.active; ws.title = "Copy"
    headers = ["Band Name - Title", "Title", "Description (Must contain CTA on shorts, unique description)",
               "Creator Comment (Must Contain CTA on shorts, unique comment and rotating Facts/Trivia/Quiz/Info)"]
    ws.append(headers)
    for c in ws[1]: c.font = Font(bold=True)
    for r in rows: ws.append([r["band"], r["title"], r["desc"], r["pin"]])
    for col, w in zip("ABCD", [42, 60, 95, 80]):
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    ws2 = wb.create_sheet("Audit")
    ws2.append(["Check", "Result"])
    ws2.append(["Rows", len(rows)])
    ws2.append(["Problems found", len(errs)])
    for e in errs: ws2.append(["FAIL", e])
    if not errs: ws2.append(["All checks", "PASS: unique starters, SF pointers and CTAs, no play along LF titles, rotating comment formats"])
    ws2.column_dimensions["A"].width = 18; ws2.column_dimensions["B"].width = 120
    wb.save(OUT)
    print(f"saved {OUT} with {len(rows)} rows, {len(errs)} problems")
    for e in errs: print("FAIL:", e)
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main())
