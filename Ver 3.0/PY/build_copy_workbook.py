#!/usr/bin/env python3
"""Build and audit the copy workbook. Run before every delivery."""
import pathlib, re, sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "Ver 3.0/TXT/Copy_Workbook_0001_0010_And_New_Uploads.xlsx"
SONGS = ["autumn leaves","another life","masterpiece","abigail","a-m-e-r-i-c-a","immaculate misconception","x-kid","welcome to the black parade","if i'd been the one"]

def block(t, *heads):
    for h in heads:
        m = re.search(rf"## {h}[^\n]*\n.*?```text\n(.*?)```", t, re.S)
        if m: return m.group(1).strip()
    return ""

def collect():
    rows = []
    for fmt, root in [("LF", ROOT/"_All Songs/_0001 Long Form"), ("SF", ROOT/"_All Songs/_0002 Short Form")]:
        for p in root.rglob("_03 - Copy.md"):
            name = p.parent.name; num = int(name[:4])
            m = re.search(r"U - (2026-11-\d\d)", name)
            new = bool(m and m.group(1) >= "2026-11-06")
            variant = any(s in name.lower() for s in SONGS)
            recent = (fmt == "LF" and 673 <= num <= 688) or (fmt == "SF" and (2420 <= num <= 2435 or num in (467, 725)))
            if not (new or variant or recent or (fmt == "LF" and num <= 10)): continue
            t = p.read_text(encoding="utf-8", errors="ignore")
            ident = re.sub(r"\s*\[U - [^\]]+\]\s*$", "", re.sub(r"\s*\((Long|Short) Form\)\s*$", "", name[7:])).strip()
            pin = block(t, "CREATOR COMMENT TO POST", "PINNED COMMENT", "CREATOR COMMENT")
            rows.append({"band": f"{fmt} {num:04} | {ident}", "fmt": fmt, "num": num,
                         "title": block(t, "TITLE"), "desc": block(t, "DESCRIPTION"), "pin": pin, "path": str(p)})
    return sorted({r["path"]: r for r in rows}.values(), key=lambda r: (r["band"].split("| ",1)[-1].lower(), r["fmt"], r["num"]))

def first3(s):
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()[:3])

def audit(rows):
    errs = []
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
