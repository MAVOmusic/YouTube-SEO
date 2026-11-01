# _All Songs - folder convention

Screenshots uploaded from YouTube Studio, one folder per video, in
UPLOAD CHRONOLOGY (oldest first). This numbering is NOT the same as the
canonical song IDs in `Ver 3.0/bands/` - see the note at the bottom.

## Layout

```
_All Songs/
  0000 - Channel Analytics/          channel-level captures, one per day
  0001 - 0010/                       songs 0001-0010
  0011 - 0020/                       songs 0011-0020 (empty, .gitkeep)
  0021 - 0030/                       songs 0021-0030 (empty, .gitkeep)
```

Uploads are grouped in **buckets of ten** so the folder list stays readable.

When the library grows past 0100, the buckets get one more level:

```
_All Songs/
  0001 - 0100/
    0001 - 0010/
    0011 - 0020/
    ...
```

Nothing reads these paths programmatically - the tools in `Ver 3.0/PY/` only
read `banks/`, `TXT/` and the kit - so buckets can be added or renamed freely.

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

Channel-order audit records (what was found, what the copy should be) live in
`Ver 3.0/TXT/Channel_Order_Audit_Log.txt`, keyed `CO-NNNN`.
