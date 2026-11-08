# _All Songs - folder convention

Screenshots uploaded from YouTube Studio, one folder per video, in
UPLOAD CHRONOLOGY (oldest first). This numbering is NOT the same as the
canonical song IDs in `Ver 3.0/bands/` - see the note at the bottom.

## Layout (restructured 01-11-2026)

```
_All Songs/
  0000 - Channel Analytics/          channel-level captures, one per day (top level)
  _0001 Long Form/
    0001 - 0010/                     songs 0001-0010
    0011 - 0020/                     songs 0011-0020
    0021 - 0030/                     songs 0021-0030 (empty, .gitkeep)
  _0002 Short Form/                  all short form videos (empty, .gitkeep)
```

The two underscore prefixes sort to the top of the folder list and keep the two
formats apart, because they are audited for completely different reasons:

| Folder | Why it is audited |
| --- | --- |
| `_0001 Long Form` | eligibility, watch time, monetisation, full copy rebuild |
| `_0002 Short Form` | reach, retention-at-3s, which long form each Short chains to |

**Long form is being audited first, in upload order.** Shorts are queued and
will not be touched until the long form walk is done. When shorts start, every
Short gets mapped to the long form it should chain to - that mapping is part of
the audit, not an afterthought.

Uploads are grouped in **buckets of ten** inside the format folder so the list
stays readable. When the library grows past 0100, the buckets get one more
level:

```
_All Songs/
  _0001 Long Form/
    0001 - 0100/
      0001 - 0010/
      0011 - 0020/
      ...
```

Nothing reads these paths programmatically - the tools in `Ver 3.0/PY/` only
read `bands/`, `TXT/` and the kit - so folders can be added or renamed freely.
Historical log entries keep the paths they were written with. Do not rewrite
them.

## Inside each song folder

```
NNNN - Artist - Song (Format)/
  _01 - Main Info/        Details, Pinned, Tags screenshots
  _02 - Analytics/
    _01 - Overview/
    _02 - Reach/
    _03 - Engagement/
    _04 - Audience/
    _05 - Revenue/
```

## Important: two numbering systems

| System | Meaning | Where |
| --- | --- | --- |
| `_All Songs/NNNN` | upload chronology on the channel | here |
| `bands/NNNN` | canonical song ID | `Ver 3.0/bands/` |

They do NOT match. Upload 0001 is Burzum - Autumn Leaves, while canonical
package 0001 is Squeeze - Cool for Cats. Never conflate them, and never use an
`_All Songs` number to look up a package.

Folder NAMES are also unreliable as a record of the video. Reconcile by video ID
and view count. `0007` still carries a double space after the dash.

Channel-order audit records (what was found, what the copy should be) live in
`Ver 3.0/TXT/Channel_Order_Audit_Log.txt`, keyed `CO-NNNN`.

## Reviewed video folder names

For the current song-by-song review, mark a completed individual video folder
as `ID - Artist - Song [U - YYYY-MM-DD]`. The date is the review date in the
Europe/London timezone (including daylight saving time). Record the exact review
time and timezone in the review file and Songs Done list rather than the folder
name. `U` means reviewed, not that a change was made in YouTube Studio. Legacy
`(Long Form)` / `(Short Form)` and earlier `[UPDATED ... UK]` names remain
recognised by the catalogue checker. Keep snapshots, copy, path references and
review records together when renaming.
