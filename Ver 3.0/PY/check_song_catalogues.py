#!/usr/bin/env python3
"""Check chronological catalogue coverage against video folders and saved copy.

This is a consistency check, not evidence that a reservation was uploaded, that
an identity is correct, or that a title is live. Curated snippet-only rows and
Studio status changes still require human updates.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
CONFIGS = (
    ("long", "Long Form 0001 - 1000.md", "_0001 Long Form", "Long Form", 1000),
    ("short", "Short Form 0001 - 3000.md", "_0002 Short Form", "Short Form", 3000),
)
ROW = re.compile(r"^\| (\d{4}) \| ((?:\\\||[^|])*) \| ((?:\\\||[^|])*) \|$")
TITLE = re.compile(r"^## TITLE\b[^\n]*\n\s*```(?:text)?\s*\n(.*?)\n```", re.I | re.M | re.S)


def unescape(value):
    return value.strip().replace("\\|", "|")


def check(root=ROOT):
    errors = []
    for kind, catalogue, folder, label, maximum in CONFIGS:
        path = root / catalogue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            errors.append(f"{catalogue}: {exc}")
            continue
        rows = {}
        for line in lines:
            match = ROW.match(line)
            if not match:
                continue
            number = int(match[1])
            if number in rows:
                errors.append(f"{catalogue}: duplicate {number:04}")
            rows[number] = (unescape(match[2]), unescape(match[3]))
        expected = set(range(1, maximum + 1))
        if set(rows) != expected:
            errors.append(f"{catalogue}: missing {sorted(expected-set(rows))}, unexpected {sorted(set(rows)-expected)}")
        seen = set()
        video_root = root / "_All Songs" / folder
        for video in video_root.glob("*/*/*"):
            if not video.is_dir():
                continue
            match = re.match(r"^(\d{4}) - (.+?) \(" + re.escape(label) + r"(?: - .*?)?\)$", video.name)
            if not match:
                continue
            number, identity = int(match[1]), match[2].strip()
            if not 1 <= number <= maximum:
                continue
            if number in seen:
                errors.append(f"{folder}: duplicate folder number {number:04}")
            seen.add(number)
            # One legacy folder censors the artist name; the reviewed copy does not.
            if kind == "short" and number == 9 and identity == "Alien F_cker - Arabic UFO Party":
                identity = "Alien Fucker - Arabic UFO Party"
            row = rows.get(number)
            if not row:
                continue
            displayed = re.sub(r" \[reserved\]$", "", row[0])
            if displayed != identity:
                errors.append(f"{catalogue}: {number:04} identity differs from {video}")
            copy = video / "_03 - Copy.md"
            if copy.exists():
                match = TITLE.search(copy.read_text(encoding="utf-8"))
                if not match:
                    errors.append(f"{copy}: cannot extract title")
                elif row[1] != match[1].strip():
                    errors.append(f"{catalogue}: {number:04} title differs from {copy}")
        print(f"{catalogue}: {len(rows)} numbered rows; {len(seen)} video folders checked")
    return errors


def main():
    errors = check()
    for error in errors:
        print("ERROR:", error, file=sys.stderr)
    if errors:
        return 1
    print("Catalogue consistency passed. Manual source and publication verification remain necessary.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
