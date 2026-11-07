# MAVOmusic (@mavomusicyt) — YouTube SEO Workspace

Repository-hosted home of the MAVOmusic SEO rehabilitation workspace (fingerstyle bass covers / Rocksmith 2014 playthroughs).

## Layout

| Path | What it is |
|---|---|
| `Test Image.jpg` | The **§28 vision probe**. Read this first in any new session: if the agent cannot describe it, the chat has no vision and cannot run the Studio-screenshot recheck workflow — stop there. |
| `Ver 3.0/` | **THE ACTIVE WORKSPACE.** All work happens here. |
| `Ver 2.68/` | **FROZEN ARCHIVE** of the last chat-paste release (also holds the original `workspace-*.zip` upload). Never edit it or run its tools — it is the rollback point. |
| `Long Form 0001 - 1000.md` | Browsable chronological long-form catalogue, including provisional reservations. |
| `Short Form 0001 - 3000.md` | Browsable chronological Shorts catalogue, including provisional reservations. |

Update the relevant catalogue whenever an upload identity or prepared title is added or changed. The user confirms the screenshot page ranges identify fixed chronological IDs. Keep titles from the earlier AI process as N/A until this process reviews and accepts them or creates replacements. Keep planned reservations marked and never infer missing identities from the legacy canonical numbering. `Ver 3.0/PY/check_song_catalogues.py` checks numbered rows and known video folders/copy titles; it does not establish publication, identity, or completeness of screenshots.

## Inside `Ver 3.0/`

```
CONTEXT_BLOCK.txt        master ruleset + current status (AUTHORITY: wins over every other file)
MAVO_PROJECT_LOG.txt     long-form project history, doctrine, chronological progress table
MAVO_VERSION_LOG.txt     per-version changelog (Ver 1.01 -> 3.0)
Matched_Shorts_To_Cross_Check.txt
MAVOmusic_Track_History.csv / .xlsx   308-record sheet, kept in sync by PY/generate_track_history.py
bands/<Letter>/<Artist>/<Song>/<NNNN>/<DD-MM-YYYY>.md   308 SEO packages
PY/                      tools (root-portable) + requirements.txt
TXT/                     analytics stores, references, recovery containers
To Attach/               per-chat paste kit (00-23), auto-built by PY/refresh_kit.py
Under Review/            THE master under-review audit
Whitelist/               THE approved Shorts-ID whitelist
IMAGES/                  transient evidence + inherited 0151-0154 panel receipts
verify.sh                two-tier pre-ship gate
```

## Quick start

```bash
pip install -r "Ver 3.0/PY/requirements.txt"   # openpyxl (only dependency)
cd "Ver 3.0"
python3 PY/generate_track_history.py     # CSV + XLSX
python3 PY/generate_reference_txts.py    # TXT/{Titles,Descriptions,Pinned_Comments,Tags}.txt
python3 PY/build_master_under_review.py  # Under Review/ + Whitelist/
python3 PY/repack.py                     # Recovery containers + round-trip check
python3 PY/refresh_kit.py                # To Attach/ kit, byte-verified
bash verify.sh                           # ALL GATES GREEN ✓  (exits 1 on any violation)
```

Tools locate the workspace from their own path, so they run from any directory or sandbox. Override with `MAVO_ROOT=/some/path` if ever needed.

## Gate rules (Ver 3.0)

* **Tier 1 — `PY/verify.py`**: title-opener / description / pinned-comment / gear-line uniqueness, `**Folder Location:**` byte-match, artist letter convention, tidy root. **Fails the build.**
* **Tier 2 — `PY/diversity_guard.py`**: Section 21 anti-repetition caps, link + pin + tag-box policy, Section 20 technique wording, retired phrases, tracking-ID leaks.

Nothing ships to YouTube Studio unless both tiers are green.
