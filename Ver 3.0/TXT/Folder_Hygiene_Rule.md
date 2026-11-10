# Folder hygiene rule: what counts as a done song folder

Standing rule from the user, 2026-11-10. Anything inside a song folder that has not been worked in the new batches is a redundant image and must never be counted as done. The user pastes fresh information into emptied folders later.

## What is protected

A song folder keeps its screenshots only if it qualifies under at least one of these:

- It carries a review marker `[U - YYYY-MM-DD]` in the folder name.
- Its ID is 0001 to 0009 in either format, together with the long form and short form edits of those uploads.
- It received files in a commit dated 2026-11-06 or later. This is the reliable test, because a new upload does not always get a marker and a folder can sit at an old ID.
- It is the song currently being processed, whatever its ID or age.

The git test is the important one. The first pass of this cleanup used only markers and ID thresholds and missed 22 folders that had screenshots uploaded between 2026-11-08 and 2026-11-10. Those 22 were restored intact from git before anything was committed. Use `git log --since=2026-11-06 --diff-filter=A --name-only` as the primary protection check, never the folder name alone.

## What gets removed

For every other song folder under `_All Songs`:

- Delete every screenshot and every non ASCII file. That covers `_01 - Main Info`, `_02 - Analytics` and their subfolders.
- Keep `_03 - Copy.md`. It is the only file that survives.
- If the folder has no `_03 - Copy.md`, add `.gitkeep` so the folder stays tracked and the user can paste new information into it.

Nothing is deleted outside `_All Songs`. Channel level analytics, `Band Info`, `Ver 3.0` records and the root reference lists are untouched.

## Results of the 2026-11-10 run

| Item | Count |
| --- | --- |
| Song folders scanned | 254 |
| Folders emptied | 89, all long form |
| Screenshots deleted | 964 |
| Folders restored after the git check | 22 |
| Folders left intact, all formats | 165 |
| `_03 - Copy.md` files removed | 0 |

Every emptied folder kept a `_03 - Copy.md`, so no `.gitkeep` was needed in the end. The 502 existing `.gitkeep` files, which mark block and range folders, were left alone.

## The 22 restored folders

All of these had files added or edited in commits dated 2026-11-06 or later, so they are new work and were restored from git after the first pass:

Long form 0101, 0102, 0103, 0104, 0105, 0106, 0107, 0108, 0109, 0110, 0167, 0262, 0643.

Short form 0054, 0068, 0243, 1434, 1553, 1803, 1912, 2008, 2390.

The blocks above ID 670 in long form and above 2410 in short form were checked separately. All 52 long form and 52 short form folders in those ranges were uploaded between 2026-11-06 and 2026-11-08, so they are new batch uploads and stay untouched.

## How to repeat it

1. List the additions since the cutoff: `git log --since=2026-11-06 --diff-filter=A --name-only --format='' -- '_All Songs/_0001 Long Form' '_All Songs/_0002 Short Form'`.
2. Cross check deletions and modifications the same way with `--diff-filter=D` and `--diff-filter=M`.
3. Remove files only from folders that appear in none of those lists, carry no marker and sit outside 0001 to 0009.
4. Re run the same `git log` check after the deletion but before committing, comparing against the list of folders that were emptied. Any overlap means a restore is needed.

## Standing rule for processing a song

A song is processed only when the user supplies its status list, in this shape:

```
Song name:
ID - Genre Added, No Pins [link to folder]
ID - Genre Added, Comment pinned [link to folder]
```

One line per ID, status first, folder link last, and the pin state stated every time. Nothing is processed from analytics alone.

## Related records

- `Ver 3.0/TXT/Green_Day_X-Kid_IDs_And_Genre_Playlists.md` holds the X-Kid ID map, genre copy and the live status of the five X-Kid folders.
- `Ver 3.0/TXT/Play_Along_Series_ID_Map.md` maps every indexed ID for play-along songs 0003 to 0010.
